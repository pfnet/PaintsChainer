class OSHelper:
    
    def detect_environment():
        import os
        if os.name == 'nt':

            if not 'INCLUDE' in os.environ:
                print('Include Path INCLUDE for Windows Kit not assigned. Please edit and use run_python.bat or run_exe.bat.')

            if not 'LIB' in os.environ:
                print('Include Path LIB for Windows Kit is not assigned.  Please edit and use run_python.bat or run_exe.bat.')
