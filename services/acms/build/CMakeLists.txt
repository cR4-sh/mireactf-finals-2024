cmake_minimum_required(VERSION 3.10)
project(ACMS)

set(CMAKE_C_COMPILER "/usr/bin/gcc")

add_library(pqlib SHARED IMPORTED)
set_property(TARGET pqlib PROPERTY
             IMPORTED_LOCATION "/usr/lib/x86_64-linux-gnu/libpq.so")

add_executable(acms "src/main.c" "src/acms_message.c" "src/acms_command_handlers.c" "src/acms_devices.c")
target_link_libraries(acms PUBLIC pqlib)
target_include_directories(acms PUBLIC "/usr/include/postgresql")
target_include_directories(acms PUBLIC "headers")
target_compile_options(acms PUBLIC "-g")