from cx_Freeze import setup, Executable

base = None    

executables = [Executable("NightLetterApp19.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "NightLetterApp",
    options = options,
    version = "2.0 ",
    description = 'Testing python exe conversion functionality',
    executables = executables
)