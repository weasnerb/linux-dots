local mainMod = "SUPER"

--
-- Display
--
-- See https://wiki.hypr.land/Configuring/Basics/Monitors/ for more
local monitorLeft = "DP-2"
local monitorCenter = "DP-1"
local monitorRight = "DP-3"

hl.monitor({ output = monitorLeft, mode = "2560x1440@143.998", position = "0x0", scale = 1 })
hl.monitor({ output = monitorCenter, mode = "2560x1440@143.998", position = "2560x0", scale = 1 })
hl.monitor({ output = monitorRight, mode = "2560x1440@59.951", position = "5120x0", scale = 1 })

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
