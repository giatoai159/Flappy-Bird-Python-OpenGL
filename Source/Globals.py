display = [650, 850]
# Vertex shader
vertex_shader_code = open("Shaders/simple_vertex_shader.txt", "r")
# Fragment shader
fragment_shader_code = open("Shaders/simple_fragment_shader.txt", "r")
# Game var
fps = 60

scroll_speed = 4
gravity = 8
gravity_speed = 0.5
jump_height = 13

leeway = 10
pipe_gap = 375
pipe_frequency = 1500 # milliseconds


