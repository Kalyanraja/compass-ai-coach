      * SYNTHETIC FIXTURE - COBOL-like text for unknown-stack fallback tests.
      * Not compiled, not run, not from any real system.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. NIGHTLY.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE ASSIGN TO INFILE.
           SELECT OUT-FILE ASSIGN TO OUTFILE.
       DATA DIVISION.
       FILE SECTION.
       FD  IN-FILE.
       01  IN-REC              PIC X(80).
       FD  OUT-FILE.
       01  OUT-REC             PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-EOF              PIC X VALUE 'N'.
       01  WS-COUNT            PIC 9(7) VALUE ZERO.
       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN INPUT IN-FILE OUTPUT OUT-FILE
           PERFORM UNTIL WS-EOF = 'Y'
               READ IN-FILE
                   AT END MOVE 'Y' TO WS-EOF
                   NOT AT END
                       ADD 1 TO WS-COUNT
                       MOVE IN-REC TO OUT-REC
                       WRITE OUT-REC
               END-READ
           END-PERFORM
           DISPLAY 'RECORDS COPIED: ' WS-COUNT
           CLOSE IN-FILE OUT-FILE
           STOP RUN.
