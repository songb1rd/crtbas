REM CRT VirtualMachine
REM ==================

REM ~ Constants
#define CODE_LIMIT 4096

#enum Opcode {
    Nop = 0,
    Exit,
    BinAdd,
    BinSub,
    Ret,
    Call,
}

REM :func: `crt.vm.main_loop`
REM
REM Run the virtual machine until completion.
    {_crt_vm_main_loop} LET IP% = 0
    {_crt_vm_main_loop_head} LET OP% = BYTECODE(OP%)

    #branch OP% {
        {Opcode.Exit}   => {end}
        {Opcode.Nop}    => {_crt_vm_main_loop_next}
        {Opcode.BinAdd} => {_crt_vm_main_action_bin_add}
        {Opcode.BinSub} => {_crt_vm_main_action_bin_sub}
        {Opcode.Ret}    => {_crt_vm_main_action_bin_ret}
        {Opcode.Call}   => {_crt_vm_main_action_bin_cal}
    }

    {_crt_vm_main_action_bin_add} 0
    {_crt_vm_main_action_bin_sub} 1
    {_crt_vm_main_action_bin_ret} 2
    {_crt_vm_main_action_bin_cal} 3

    {_crt_vm_main_loop_next} IP = IP + 1
    IF IP% < {CODE_LIMIT} THEN GOTO {_crt_vm_main_loop_head}
    {end} END
