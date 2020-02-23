find ./configs -name "*log" | xargs rm
find ./configs -name "*db" | xargs rm
find ./configs -name "*link.private.pem" | xargs rm
find ./configs -name "*.storage"  | xargs rm
find ./configs -name "*management_sock"  | xargs rm
