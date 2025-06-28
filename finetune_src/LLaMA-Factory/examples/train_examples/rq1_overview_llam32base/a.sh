find ./ -name '*yaml' -exec bash -c '
  for file; do
    newfile="${file//_full/}"
    if [[ "$file" != "$newfile" ]]; then
      mv -v "$file" "$newfile"
    fi
  done
' bash {} +

