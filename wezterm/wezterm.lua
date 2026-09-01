-- Flava WezTerm config — same look and keybindings on Windows/WSL and macOS.
--
-- The only platform-dependent parts are the default domain (WSL on Windows, the login
-- shell everywhere else), the path separator used by resurrect's save directory, and
-- the acrylic backdrop, which is a Windows-only API.

local wezterm = require 'wezterm'
local config = wezterm.config_builder()

local triple = wezterm.target_triple
local is_windows = triple:find('windows') ~= nil
local is_mac = triple:find('darwin') ~= nil
local sep = is_windows and '\\' or '/'

-- 0. Resurrect: saves and restores workspaces/tabs/panes. On Windows this survives
--    `wsl --shutdown` and reboots, because wezterm.exe itself runs natively.
local resurrect = wezterm.plugin.require('https://github.com/MLFlexer/resurrect.wezterm')

-- State lives in the native home directory. On Windows that deliberately avoids /mnt/c,
-- where the permission model inside WSL causes save failures.
local state_dir = wezterm.home_dir .. sep .. '.local' .. sep .. 'share' .. sep
  .. 'wezterm' .. sep .. 'resurrect' .. sep
resurrect.state_manager.change_state_save_dir(state_dir)

-- Autosave every 5 minutes.
resurrect.state_manager.periodic_save({ interval_seconds = 300 })

-- resurrect_on_gui_startup does not read the .json files directly: it looks for a
-- "current_state" marker (name + type) that only write_current_state writes.
-- save_state and periodic_save never write it, so without this the auto-restore failed
-- silently every time (pcall with no notification). We refresh it after every save,
-- manual and automatic, so it always points at the latest state.
resurrect.state_manager.write_current_state('default', 'workspace')
wezterm.on('resurrect.state_manager.periodic_save.finished', function()
  resurrect.state_manager.write_current_state('default', 'workspace')
end)

-- Restore the last state automatically when WezTerm opens.
wezterm.on('gui-startup', resurrect.state_manager.resurrect_on_gui_startup)

-- 1. Default domain: WSL on Windows, the regular login shell elsewhere.
if is_windows then
  config.default_domain = 'WSL:Ubuntu'
end

-- 2. Theme and typography
config.color_scheme = 'Catppuccin Mocha'
config.font = wezterm.font('JetBrains Mono')
config.font_size = is_mac and 13.0 or 11.0

-- 3. Transparency and glass effect
config.window_background_opacity = 0.70
if is_windows then
  config.win32_system_backdrop = 'Acrylic'
elseif is_mac then
  config.macos_window_background_blur = 30
end

-- 4. Clean borders and inner padding
config.window_decorations = 'RESIZE'
config.window_padding = { left = 12, right = 12, top = 12, bottom = 12 }

-- 5. Resurrect keybindings
config.keys = {
  -- ALT+W (OPT+W on macOS): save the current workspace by hand.
  -- Lists the already-saved workspaces, so you can overwrite one, plus a "+ New..."
  -- entry to save under a name that does not exist yet.
  {
    key = 'w',
    mods = 'ALT',
    action = wezterm.action_callback(function(win, pane)
      local function do_save(w, name)
        local state = resurrect.workspace_state.get_workspace_state()
        resurrect.state_manager.save_state(state, name)
        resurrect.state_manager.write_current_state(name, 'workspace')
        w:toast_notification('resurrect.wezterm', 'Workspace saved as "' .. name .. '"', nil, 4000)
      end

      local files = wezterm.glob(state_dir .. 'workspace' .. sep .. '*.json')
      local choices = { { label = '+ New...', id = '__new__' } }
      for _, f in ipairs(files) do
        local name = f:match('([^\\/]+)%.json$')
        if name then
          table.insert(choices, { label = name, id = name })
        end
      end

      win:perform_action(
        wezterm.action.InputSelector {
          title = 'Save workspace (pick one to overwrite, or "+ New...")',
          fuzzy = true,
          choices = choices,
          action = wezterm.action_callback(function(win2, pane2, id, label)
            if not id then
              return -- cancelled
            end
            if id == '__new__' then
              win2:perform_action(
                wezterm.action.PromptInputLine {
                  description = 'Name for the new saved workspace',
                  action = wezterm.action_callback(function(win3, pane3, line)
                    if line == nil or line == '' then
                      return -- cancelled or empty
                    end
                    do_save(win3, line)
                  end),
                },
                pane2
              )
            else
              do_save(win2, id)
            end
          end),
        },
        pane
      )
    end),
  },
  -- ALT+R: pick and restore a saved state (fuzzy finder)
  {
    key = 'r',
    mods = 'ALT',
    action = wezterm.action_callback(function(win, pane)
      resurrect.fuzzy_loader.fuzzy_load(win, pane, function(id, label)
        local type = string.match(id, '^([^/]+)')
        id = string.match(id, '([^/]+)$')
        id = string.match(id, '(.+)%..+$')
        local opts = {
          relative = true,
          restore_text = true,
          on_pane_restore = resurrect.tab_state.default_on_pane_restore,
        }
        if type == 'workspace' then
          local state = resurrect.state_manager.load_state(id, 'workspace')
          resurrect.workspace_state.restore_workspace(state, opts)
        elseif type == 'window' then
          local state = resurrect.state_manager.load_state(id, 'window')
          resurrect.window_state.restore_window(win, state, opts)
        elseif type == 'tab' then
          local state = resurrect.state_manager.load_state(id, 'tab')
          resurrect.tab_state.restore_tab(pane:tab(), state, opts)
        end
      end)
    end),
  },
}

return config
