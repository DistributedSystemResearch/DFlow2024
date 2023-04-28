cmake_minimum_required(VERSION 3.11)

project(StoneFlow VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O2")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
include(FindCPR)


# include_directories("/usr/local/include")
# include_directories("usr/local/lib")
find_package(ZLIB REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(wfrest REQUIRED)
find_package(workflow REQUIRED)
#find_package(cpr REQUIRED)
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

include_directories(${workflow_INCLUDE_DIRS})
include_directories(${wfrest_INCLUDE_DIRS})

file(GLOB stoneflow_utils_SRC    "src/utils/*.h"   "src/utils/*.cc")
add_library(stoneflow_utils ${stoneflow_utils_SRC} )

include(FetchContent)
FetchContent_Declare(cpr
                         GIT_REPOSITORY git@github.com:lambda7xx/cpr.git
                         GIT_TAG  beb9e98806bb84bcc130a2cebfbcbbc6ce62b335) # The commit hash for 1.7.2. Replace with the latest from: https://github.com/libcpr/cpr/releases
FetchContent_MakeAvailable(cpr)

file(GLOB local_scheduler_SRC "src/local_scheduler/*.h"   "src/local_scheduler/*.cc")
add_library(local_scheduler  ${local_scheduler_SRC} )

add_executable(main ${local_scheduler_SRC} )
target_include_directories(main PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/local_scheduler)




target_link_libraries(main   PRIVATE stoneflow_utils  ${workflow_LIBRARIES} ${wfrest_LIBRARIES}  workflow wfrest z PRIVATE cpr::cpr PRIVATE Threads::Threads )