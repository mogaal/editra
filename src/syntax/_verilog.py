###############################################################################
# Name: verilog.py                                                            #
# Purpose: Configuration module for Verilog HDL language                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: verilog.py
AUTHOR: Cody Precord
@summary: Lexer configuration module for Verilog Hardware Description Language
          and System Verilog programming languages. Much help in creating this
          module from Tim Corcoran.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: _verilog.py 62364 2009-10-11 01:02:12Z CJP $"
__revision__ = "$Revision: 62364 $"

#-----------------------------------------------------------------------------#
# Imports
import wx.stc as stc

# Local Imports
import synglob
import syndata

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
V_KEYWORDS = (0, "always and assign attribute begin case casex casez deassign "
                 "default defparam disable edge else end endattribute endcase "
                 "endfunction endprimitive endmodule endspecify endtable "
                 "endtask event for force forever fork function if ifnone "
                 "initial inout input join medium module large macromodule "
                 "negedge output parameter posedge primitive release repeat "
                 "scalared signed small specify specparam strength table task "
                 "unsigned vectored wait while")

V_TYPES = (1, "buf bufif0 bufif1 cmos highz0 highz1 integer nand nmos nor not "
              "notif0 notif1 or pmos pull0 pull1 pulldown pullup rcmos real "
              "realtime reg rnmos rpmos rtran rtranif0 rtranif1 strong0 "
              "strong1 supply0 supply1 time tran tranif0 tranif1 tri tri0 tri1 "
              "triand trior triregwand weak0 weak1 wire wor xnor xor")

TASKS = (2, "$display $displayb $displayh $displayo $monitor $monitorb "
            "$monitorh $monitoro $monitoroff $monitoron $strobe $strobeb "
            "$strobeh $strobeo $write $writeb $writeh $writeo $fclose "
            "$fdisplay $fdisplayb $fdisplayh $fdisplayo $ferror $fflush $fgetc "
            "$fgets $fmonitor $fmonitorb $fmonitorh $fmonitoro $fopen $fread "
            "$fscanf $fseek $fstrobe $fstrobeb $fstrobeh $fstrobeo $ftell "
            "$fwrite $fwriteb $fwriteh $fwriteo $readmemb $readmemh $rewind "
            "$sdf_annotate $sformat $sscanf $swrite $swriteb $swriteh $swriteo "
            "$ungetc $printtimescale $timeformat $finish $stop "
            "$async$and$array $async$nand$array $async$nor$array "
            "$async$or$array $sync$and$array $sync$nand$array $sync$nor$array "
            "$sync$or$array $async$and$plane $async$nand$plane "
            "$async$nor$plane $async$or$plane $sync$and$plane $sync$nand$plane "
            "$sync$nor$plane $sync$or$plane $q_add $q_exam $q_full "
            "$q_initialize $q_remove $realtime $stime $time $bitstoreal "
            "$realtobits $itor $rtoi $signed $unsigned $dist_chi_square "
            "$dist_erlang $dist_exponential $dist_normal $dist_poisson $dist_t "
            "$dist_uniform $random $test$plusargs $value$plusargs $dumpall "
            "$dumpfile $dumpflush $dumplimit $dumpoff $dumpon $dumpports "
            "$dumpportsall $dumpportsflush $dumpportslimit $dumpportsoff "
            "$dumpportson $dumpvars")

USER_KW = (3, "")

#---- System Verilog Extensions ----#
SV_KEYWORDS = ("alias always_comb always_ff always_latch assert assume "
               "automatic before bind bins binsof bit break constraint "
               "covergroup coverpoint clocking const context continue cover "
               "cross dist do endgroup endinterface endpackage endprogram "
               "endproperty endsequence expect export extends extern final "
               "first_match foreach forkjoin iff ignore_bins illegal_bins "
               "import inside interface intersect join_any join_none modport "
               "new null package priority process program property pure "
               "randcase randsequence ref return sequence solve super this "
               "throughout timeprecision timeunit type unique wait_order "
               "wildcard with within")

SV_TYPES = ("byte chandle class endclass enum int local logic longint packed "
            "protected rand randc shortint shortreal static string struct "
            "tagged typedef union var virtual void")

SV_TASKS = ("$error $fatal $info $warning $onehot $onehot0 $isunknown $sampled "
           "$rose $fell $stable $countones $bits $isunbounded $typename "
           "$coverage_control $coverage_get_max $coverage_get $coverage_merge "
           "$coverage_save $unpacked_dimensions $dimensions $left $right "
           "$low $high $increment $size $asserton $assertoff $assertkill "
           "$psprintf")

#---- End System Verilog Extensions ----#

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [('STC_V_COMMENT', 'comment_style'),
                ('STC_V_COMMENTLINE', 'comment_style'),
                ('STC_V_COMMENTLINEBANG', 'comment_style'),
                ('STC_V_DEFAULT', 'default_style'),
                ('STC_V_IDENTIFIER', 'default_style'),
                ('STC_V_NUMBER', 'number_style'),
                ('STC_V_OPERATOR', 'operator_style'),
                ('STC_V_PREPROCESSOR', 'pre_style'),
                ('STC_V_STRING', 'string_style'),
                ('STC_V_STRINGEOL', 'stringeol_style'),
                ('STC_V_USER', 'default_style'),
                ('STC_V_WORD', 'keyword_style'),
                ('STC_V_WORD2', 'keyword2_style'),
                ('STC_V_WORD3', 'scalar_style')]

#---- Extra Properties ----#
FOLD = ("fold", "1")
FOLD_CMT = ("fold.comment", "1")
FOLD_PRE = ("fold.preprocessor", "1")
FOLD_COMP = ("fold.compact", "1")
FOLD_ELSE = ("fold.at.else", "0")
FOLD_MOD = ("fold.verilog.flags", "0")

#-----------------------------------------------------------------------------#

class SyntaxData(syndata.SyntaxDataBase):
    """SyntaxData object for Verilog and SysVerilog""" 
    def __init__(self, langid):
        syndata.SyntaxDataBase.__init__(self, langid)

        # Setup
        self.SetLexer(stc.STC_LEX_VERILOG)

    def GetKeywords(self):
        """Returns Specified Keywords List """
        if self.LangId == synglob.ID_LANG_VERILOG:
            return [V_KEYWORDS, V_TYPES, TASKS]
        else:
            return [(0, " ".join([V_KEYWORDS[1], SV_KEYWORDS])),
                    (1, " ".join([V_TYPES[1], SV_TYPES])),
                    (2, " ".join([TASKS[1], SV_TASKS]))]

    def GetSyntaxSpec(self):
        """Syntax Specifications """
        return SYNTAX_ITEMS

    def GetProperties(self):
        """Returns a list of Extra Properties to set """
        return [FOLD]

    def GetCommentPattern(self):
        """Returns a list of characters used to comment a block of code """
        return [u'//']
