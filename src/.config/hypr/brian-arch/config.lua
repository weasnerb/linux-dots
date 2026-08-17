local mainMod = "SUPER"

--
-- Display
--
-- See https://wiki.hypr.land/Configuring/Basics/Monitors/ for more
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1.25 })

--
-- Workspaces:
--

-- Switch workspaces with mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

--
-- Screen Brightness
--
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("light -A 5"))
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("light -U 5"))

--
-- Keyboard Backlighting
--
hl.bind("XF86WakeUp + space", hl.dsp.exec_cmd("$HOME/.config/sway/custom-scripts/keyboard_backlight.py"))
