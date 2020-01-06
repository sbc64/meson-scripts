find ./configs -name "*log" | grep -v pkg | grep -v vim | grep -v oh-my  | xargs rm
find ./configs -name "*db" | grep -v pkg | grep -v vim | grep -v oh-my | xargs rm
find ./configs -name "*link.private.pem" | grep -v Meson | xargs rm
find ./configs -name "*.storage"  | xargs rm
find ./configs -name "*.db"  | xargs rm
find ./configs -name "*management_sock"  | xargs rm
