REM CRT
REM ===
REM
REM A really basic C runtime and interpreter.
REM ----------------------------------------
REM
REM ~ Courtesy of Songer :D

REM :func:`crt.main`
REM
REM <inline comment> `arg$` is assumed to be the target filepath.
    {_crt_start} OPEN "test.c", AS #1

    REM <inline comment> once we've hit EOF that means everything is in the VM
    {_crt_start_test_file_eof} IF eof(1) = -1 THEN GOTO {_crt_vm_main_loop}

    {_crt_start_file_readline} INPUT# 1, LINE$
    GOSUB {_crt_parse_line}
    GOTO {_crt_start_test_file_eof}
    GOTO {_crt_start_file_readline}

REM :func:`crt.parse_line`
REM
REM Deal with one line in some ambigous context.
REM
REM <todo> Implement source line trimming
    {_crt_parse_line} LET INDEX% = 0
    {_crt_parse_line_read_char} LET CURSOR$ = mid$(LINE$, INDEX, 1)

    REM <inline comment> Special case brances:
    REM IF CURSOR$ = " " THEN GOTO {parse_char_whitepsace}
    REM IF CURSOR$ = "/" THEN GOTO {parse_char_forward_slash}

    INDEX = INDEX + 1
    IF INDEX < LEN(LINE$) THEN GOTO {_crt_parse_line_read_char}
    RETURN

    #branch CURSOR$ {
        " " => {_crt_parse_line_read_char}
        "/" => {_crt_parse_line_read_char}
    }

#include "virtual_machine.bas"

{end} END
