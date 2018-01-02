# bash completion for raptly

# Completion function
_raptly ()
{
  # Current completion word
  local cur
  cur=${COMP_WORDS[COMP_CWORD]}

  # Array containing completions
  COMPREPLY=()
  COMPREPLY=( $( compgen -W 'create check deploy undeploy test stage release version show' -- $cur ) )

  return 0
}

complete -F _raptly -o filenames raptly