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
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl set +5%"))
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl set 5%-"))

--
-- Keyboard Backlighting
--
-- No bind needed: Fn+Space is handled by the ThinkPad's firmware (verified
-- 2026-11-26 with the bind removed). The old "XF86WakeUp + space" bind never
-- worked as intended anyway: XF86WakeUp (the Fn key) isn't a modifier, so the
-- Lua loader dropped it and registered a bind on plain `space`.
