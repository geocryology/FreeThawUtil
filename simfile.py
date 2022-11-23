import re


DEF = "definition"
COMMENT = "comment"
MLCOMS = "multi-line comment start"
MLCOMB = "multi-line comment body"
MLCOME = "multi-line comment end"
IMPORT = "import"
HFT = "hidden from-to"
FT = "from-to"
WS = "whitespace only"


class FreeThawSim:

    def __init__(self, file):
        self.file = file
        self._lines = self._read(file)

    @property
    def lines(self):
        return self._lines

    def _read(self, file):
        with open(file) as f:
            lines = f.readlines()
            matched_lines = []
            
            for l in lines:                
                matched_lines.append(Line(l))

        return matched_lines        

    def write(self, file):
        lines = [line.text for line in self.lines]
        
        with open(file, 'w') as f:
            f.writelines(lines)

    def set_variable(self, key, value):
        L = self.get_variable_line(key)
        if L:
            L.set_variable(value)
            return

    def get_variable_line(self, key):
        for L in self.lines:
            if key == L.get("key"):
                return L

    def get_fromto_line(self, key):
        for L in self.lines:
            if key == L.get("from"):
                return L

    def comment(self, parameter):
        for L in self.lines:
            if parameter == L.get("from"):
                L.comment()
                return
    
    def uncomment(self, parameter):
        for L in self.lines:
            if parameter == L.get("from"):
                L.uncomment()
                return


class Line:

    def __init__(self, text):
        self._type = None
        self._commented = None
        self._text = text
        self._unknown = None
        self._dict = {}
        self.parse(text)

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"<Line ({self._type}): {self._text}>"
    
    @property
    def text(self):
        return self._text

    def get(self, key):
        return self._dict.get(key)

    def parse(self, text):
        for t, p in patterns.items():
                
            if match:=p.match(text):
                self._unknown = False
                self._type = t
                self._dict = {key.strip(): value.strip() for key, value in match.groupdict().items()}
                
                if t in [MLCOMS, MLCOMB, MLCOME, COMMENT, HFT]:
                    self._commented = True
                else:
                    self._commented = False
                
                return

        self._unknown = True
        self._type = "unknown"

    def comment(self):
        if self._commented or self._commented is None:
            return
        self._text = "//" + self._text
        self._commented = True

    def uncomment(self):
        if not self._commented:
            return
        self._text = self._text[2:]
        self._commented = False

    def set_variable(self, value):
        if not self._type == DEF:
            return
        
        self._dict["value"] = value
        
        if isinstance(value, str):
            self._text = f'def {self.get("key")} = "{value}"\n'
        else:
            self._text = f'def {self.get("key")} = {value}\n'


patterns = {
    DEF : re.compile(r"\s*def\s*(?P<key>.*)\s*=\s*(?P<value>.*)"),
    MLCOMS : re.compile(r"\s*/\*(?P<comment>.*)"),
    MLCOMB : re.compile(r"\s*\*(?P<comment>.*)"),
    MLCOME : re.compile(r"\s*(?P<comment>.*)\*/"),
    IMPORT : re.compile(r"import\s*(?P<import>.*)"),
    HFT : re.compile(r'^\s*//\s*"(?P<from>[^"]*)"\s*"(?P<to>[^"]*)"\s*$'),
    FT : re.compile(r'\s*"(?P<from>[^"]*)"\s*"(?P<to>[^"]*)"\s*$'),
    COMMENT : re.compile(r"\s*//(?P<comment>.*)"),
    WS : re.compile(r"^[\s\n]*$")
}


file = "/fs/yedoma/usr-storage/nbr512/FreeThaw/xice/OMS_Project_FreeThawXice1D-0.9/simulation/spinup_in_depth.sim"


L = FreeThawSim(file)
L.set_variable('aMin', 0.04)
L.comment("solver_spin_up_in_depth.waterDensity")
# L.write("/fs/yedoma/usr-storage/nbr512/FreeThaw/xice/OMS_Project_FreeThawXice1D-0.9/simulation/spinup_in_depth_edited.sim")


