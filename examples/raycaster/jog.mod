# Wolfenstein-style software raycaster demo (flat-colored DDA walls).
module raycaster
version 0.1.0
kind executable
jog 0.0.1

require jog_sdl ../..

# Smoke require.test resolution (test-only; ignored by build/run).
require.test mock_noop ./mocks/mock_noop
