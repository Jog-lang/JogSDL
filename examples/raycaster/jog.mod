# Wolfenstein-style software raycaster demo (flat-colored DDA walls).
module raycaster
version 0.1.0
kind executable
jog 0.0.1

require jog_sdl ../..

# std.math @link("m") does not yet flow into the consumer link line (Friction).
link.linux m
link.macos m
link.emscripten m

# Smoke require.test resolution (test-only; ignored by build/run).
require.test mock_noop ./mocks/mock_noop
