# bash completion for raptly

_raptly ()
{
    # Current completion word
    local cur prev prevprev
    cur=${COMP_WORDS[COMP_CWORD]}
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    if [ "${COMP_CWORD}" -ge 2 ]
        then
        prevprev="${COMP_WORDS[COMP_CWORD-2]}"
    fi

    COMPREPLY=()

    case "${prevprev}" in
    deploy|check)
        COMPREPLY=( $(compgen -f ${cur}) )
        return 0
        ;;
    *)
    ;;
    esac

    case "${prev}" in
    -p|--packages)
        COMPREPLY=( $(compgen -f ${cur}) )
        return 0
        ;;
    *)
    ;;
    esac

    COMPREPLY=( $( compgen -W 'create check deploy undeploy test stage release version show' -- $cur ) )

    return 0
}

complete -F _raptly -o default raptly