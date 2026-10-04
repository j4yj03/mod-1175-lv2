file(REMOVE_RECURSE
  "libysfx.a"
  "libysfx.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang ASM C CXX)
  include(CMakeFiles/ysfx.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
