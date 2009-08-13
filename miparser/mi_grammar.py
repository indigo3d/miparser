

from odict import odict
from ply import *
import mi_lexer
from mi_lexer import Entity, Value
import sys
import inspect
import re

tokens = mi_lexer.tokens

start = 'start'

precedence =  []

debug = False

def _split_rule(docstring):
    "split a grammar rule into ( type_name, [ token, token, token, .... ] )"
    # TODO : use docstring parser from PLY
    type, rule = docstring.split(':')
    return (type.strip(), [ x for x in rule.split(' ') if x] )  
        
def flag(func):
    """
    for straightforward (flag, value) combos, this decorator
    will determine which parts of the rule are the flag name and which parts
    are the values.
    
    for example, these option rules might translate to the following (flag, value) tuples:
    
        SAMPLES MOTION T_INTEGER -->  ( 'samples motion', 2 )
        TRACE boolean            -->  ( 'trace', True )
        
    a list of these tuples is then passed to the 'attrs' keyword of the NamedEntity class
    """  

    type, rules = _split_rule(func.__doc__)
    def autoflag(p):
 
        if len(p) == 2:
            p[0] = (p[1],None)
        keys = []
        for i, tok in enumerate(p[1:]):
            if not isinstance(tok,Value):
                keys.append(tok)
            else:
                break
        try:
            key = ' '.join(keys)
        except:
            if debug:
                print "autoflag failed", type
            return func(p)
        else:
            value = p[i+1:]
            if len(value)==1:
                value = value[0]
            elif len(value)==0:
                value = None
            if debug:
                print "autoflag", type, ( key, value )
            p[0] = ( key, value )
      
    autoflag.__name__ = func.__name__
    autoflag.__doc__ = func.__doc__
    autoflag.__module__ = func.__module__
    return autoflag
    
class NamedEntity(Entity):
    def __init__(self, type, text, name, data=None, attrs=() ):
        Entity.__init__(self, type, text)
        self._name = name
        if debug:
            print "namedEntity"
            for x, y in attrs:
                print '\t', x, y
        self._attrs = odict( attrs )
        self._data = data
        
    @property
    def attrs(self):
        return self._attrs 
     
    @property
    def name(self):
        return self._name
    
    @property
    def data(self):
        return self._data
# -------------- RULES ----------------

def p_start_1(p):
    '''start : _embed0_start command_list '''
    # { mi_timing(my_timer, 0); }
    
    #print "ROOT", p[2]
    p.lexer.root = p[2]
    
def p_start_2(p):
    '''start :  '''

def p__embed0_start(p):
    '''_embed0_start : '''
    # { functag = 0;
    #                           mi_api_incremental(is_incremental = miFALSE);
    #                           mi_api_private(session_depth = 0);
    #                           my_timer = mi_timing(0, 0); }

def p_boolean_1(p):
    '''boolean : ON '''
    # { $$ = miTRUE; }
    p[0] = Value('boolean', p[1], True )

def p_boolean_2(p):
    '''boolean : OFF '''
    # { $$ = miFALSE; }
    p[0] = Value('boolean', p[1], False )
    
def p_boolean_3(p):
    '''boolean : TRUE '''
    # { $$ = miTRUE; }
    p[0] = Value('boolean', p[1], True )

def p_boolean_4(p):
    '''boolean : FALSE '''
    # { $$ = miFALSE; }
    p[0] = Value('boolean', p[1], False )

def p_floating_1(p):
    '''floating : T_FLOAT '''
    # { $$ = $1; }
    p[0] = p[1]

def p_floating_2(p):
    '''floating : T_INTEGER '''
    # { $$ = $1; }
    p[0] = Value( p[1].type, p[1].text, float(p[1].data) )
        
def p_vector_1(p):
    '''vector : floating floating floating '''
    # { $$.x = $1; $$.y = $2; $$.z = $3; }

def p_vector_2(p):
    '''vector : T_VECTOR '''
    # { $$ = $1; }

def p_geovector_1(p):
    '''geovector : floating floating floating '''
    # { $$.x = $1; $$.y = $2; $$.z = $3; }

def p_geovector_2(p):
    '''geovector : T_VECTOR '''
    # { $$.z = $1.z; $$.y = $1.y; $$.x = $1.x; }

def p_color_1(p):
    '''color : floating floating floating '''
    # { $$.r = $1; $$.g = $2; $$.b = $3; $$.a = 1.0f; }

def p_color_2(p):
    '''color : floating floating floating floating '''
    # { $$.r = $1; $$.g = $2; $$.b = $3; $$.a = $4; }

def p_transform_1(p):
    '''transform : TRANSFORM floating floating floating floating floating floating floating floating floating floating floating floating floating floating floating floating '''
    # { $$[0] = $2;  $$[1] = $3;  $$[2] = $4;  $$[3] = $5;
    #                           $$[4] = $6;  $$[5] = $7;  $$[6] = $8;  $$[7] = $9;
    #                           $$[8] = $10; $$[9] = $11; $$[10]= $12; $$[11]= $13;
    #                           $$[12]= $14; $$[13]= $15; $$[14]= $16; $$[15]= $17; }
    p[0] = (p[1], tuple(p[2:]) )

def p_symbol_1(p):
    '''symbol : T_SYMBOL '''
    # { $$ = $1; }
    p[0] = p[1]
	
def p_symbol_2(p):
    '''symbol : T_STRING '''
    # { $$ = $1; }
    p[0] = p[1]

def p_opt_symbol_1(p):
    '''opt_symbol :  '''
    # { $$ = 0; }
    p[0] = p[1]

def p_opt_symbol_2(p):
    '''opt_symbol : symbol '''
    # { $$ = $1; }
    p[0] = p[1]

def p_opt_string_1(p):
    '''opt_string :  '''
    # { $$ = 0; }
    p[0] = p[1]

def p_opt_string_2(p):
    '''opt_string : T_STRING '''
    # { $$ = $1; }
    p[0] = p[1]


def p_colorclip_mode_1(p):
    '''colorclip_mode : RGB '''
    # { $$ = miIMG_COLORCLIP_RGB; }
    p[0] = p[1]

def p_colorclip_mode_2(p):
    '''colorclip_mode : ALPHA '''
    # { $$ = miIMG_COLORCLIP_ALPHA; }
    p[0] = p[1]

def p_colorclip_mode_3(p):
    '''colorclip_mode : RAW '''
    # { $$ = miIMG_COLORCLIP_RAW; }
    p[0] = p[1]

#======================================
# command list
#======================================

def p_command_list_1(p):
    '''command_list : _embed0_command_list command '''
    p[0] = [p[2]]

def p_command_list_2(p):
    '''command_list : command_list _embed1_command_list command '''
    p[0] = p[1] + [p[3]]
    
def p__embed0_command_list(p):
    '''_embed0_command_list : '''
    # { mi_api_incremental(is_incremental = miFALSE);
    #                           mi_api_private(session_depth = 0); }

def p__embed1_command_list(p):
    '''_embed1_command_list : '''
    # { mi_api_incremental(is_incremental = miFALSE);
    #                           mi_api_private(session_depth = 0); }


#======================================
# commands
#======================================

def p_command_1(p):
    '''command : set '''
    p[0] = p[1]

def p_command_2(p):
    '''command : frame '''
    p[0] = p[1]

def p_command_3(p):
    '''command : debug '''
    p[0] = p[1]

def p_command_4(p):
    '''command : call '''
    p[0] = p[1]

def p_command_5(p):
    '''command : version '''
    p[0] = p[1]

def p_command_6(p):
    '''command : incr_command '''
    p[0] = p[1]

def p_command_7(p):
    '''command : PRIVATE _embed0_command incr_command '''

def p_command_8(p):
    '''command : SESSION DEPTH T_INTEGER _embed1_command incr_command '''

def p_command_9(p):
    '''command : INCREMENTAL _embed2_command incr_command '''

def p_command_10(p):
    '''command : DELETE symbol '''
    # { mi_api_delete($2); }

def p_command_11(p):
    '''command : RENDER symbol symbol symbol '''
    # { mi_timing(my_timer, "mi scene file parsing");
    #                           mi_timing(my_timer, 0);
    #                           mi_api_render($2, $3, $4,
    #                                          mi_api_strdup(ctx->inheritance_func));
    #                           yyreturn MIYYRENDER; }

def p_command_12(p):
    '''command : VERBOSE boolean '''
    # { if (!ctx->mi_force_verbose)
    #                                 mi_set_verbosity($2? miERR_ALL & ~miERR_DEBUG
    #                                                                & ~miERR_VDEBUG
    #                                                    : miERR_FATAL|miERR_ERROR);}

def p_command_13(p):
    '''command : VERBOSE T_INTEGER '''
    # { if (!ctx->mi_force_verbose)
    #                                 mi_set_verbosity((1 << $2) - 1); }

def p_command_14(p):
    '''command : ECHO T_STRING '''
    # { mi_info("%s", $2);
    #                           mi_api_release($2); }

def p_command_15(p):
    '''command : SYSTEM T_STRING '''
    # { if ((system($2) >> 8) & 0xff)
    #                           mi_api_warning("system \"%s\" failed", $2);
    #                           mi_api_release($2); }

def p_command_16(p):
    '''command : MEMORY T_INTEGER '''
    # { mi_api_warning("memory view parameter ignored"); }

def p_command_17(p):
    '''command : CODE T_STRING '''
    # { mi_link_file_add($2, miTRUE, miFALSE, miFALSE);
    #                           mi_api_release($2); }

def p_command_18(p):
    '''command : CODE _embed3_command code_bytes_list '''
    # { mi_api_code_verbatim_end(); }

def p_command_19(p):
    '''command : LINK T_STRING '''
    # { mi_link_file_add($2, miFALSE, miFALSE, miFALSE);
    #                           mi_api_release($2); }

def p_command_20(p):
    '''command : DECLARE function_decl '''

def p_command_21(p):
    '''command : DECLARE phenomenon_decl '''

def p_command_22(p):
    '''command : DECLARE data_decl '''

def p_command_23(p):
    '''command : REGISTRY symbol _embed4_command reg_body END REGISTRY '''
    # { mi_api_registry_end(); }

def p_command_24(p):
    '''command : TOUCH symbol '''
    # { mi_api_touch($2); }

def p_command_25(p):
    '''command : NAMESPACE symbol '''
    # { mi_api_scope_begin($2); }

def p_command_26(p):
    '''command : END NAMESPACE '''
    # { mi_api_scope_end(); }

def p_command_27(p):
    '''command : ROOT symbol '''
    # { mi_api_assembly_root($2); }

def p__embed0_command(p):
    '''_embed0_command : '''
    # { mi_api_private(session_depth = 255); }

def p__embed1_command(p):
    '''_embed1_command : '''
    # { mi_api_private(session_depth = $3); }

def p__embed2_command(p):
    '''_embed2_command : '''
    # { mi_api_incremental(is_incremental = miTRUE);
    #                           mi_api_private(session_depth = 0); }

def p__embed3_command(p):
    '''_embed3_command : '''
    # { mi_api_code_verbatim_begin(); }

def p__embed4_command(p):
    '''_embed4_command : '''
    # { mi_api_registry_begin($2); }

def p_reg_body_1(p):
    '''reg_body :  '''

def p_reg_body_2(p):
    '''reg_body : reg_item reg_body '''

def p_reg_item_1(p):
    '''reg_item : VALUE symbol '''
    # { mi_api_registry_add(mi_api_strdup("value"), $2); }

def p_reg_item_2(p):
    '''reg_item : LINK symbol '''
    # { mi_api_registry_add(mi_api_strdup("link"), $2); }

def p_reg_item_3(p):
    '''reg_item : CODE symbol '''
    # { mi_api_registry_add(mi_api_strdup("code"), $2); }

def p_reg_item_4(p):
    '''reg_item : MI symbol '''
    # { mi_api_registry_add(mi_api_strdup("mi"), $2); }

def p_reg_item_5(p):
    '''reg_item : SPDL symbol '''
    # { mi_api_registry_add(mi_api_strdup("spdl"), $2); }

def p_reg_item_6(p):
    '''reg_item : ECHO symbol '''
    # { mi_api_registry_add(mi_api_strdup("echo"), $2); }

def p_reg_item_7(p):
    '''reg_item : SYSTEM symbol '''
    # { mi_api_registry_add(mi_api_strdup("system"), $2); }

def p_reg_item_8(p):
    '''reg_item : symbol symbol '''
    # { mi_api_registry_add($1, $2); }

def p_incr_command_1(p):
    '''incr_command : light '''
    p[0] = p[1]

def p_incr_command_2(p):
    '''incr_command : instance '''
    p[0] = p[1]
    
def p_incr_command_3(p):
    '''incr_command : options '''
    p[0] = p[1]

def p_incr_command_4(p):
    '''incr_command : camera '''
    p[0] = p[1]

def p_incr_command_5(p):
    '''incr_command : object '''
    p[0] = p[1]

def p_incr_command_6(p):
    '''incr_command : texture '''
    p[0] = p[1]

def p_incr_command_7(p):
    '''incr_command : profile_data '''
    p[0] = p[1]

def p_incr_command_8(p):
    '''incr_command : cprof '''
    p[0] = p[1]

def p_incr_command_9(p):
    '''incr_command : spectrum_data '''
    p[0] = p[1]

def p_incr_command_10(p):
    '''incr_command : material '''
    p[0] = p[1]

def p_incr_command_11(p):
    '''incr_command : instgroup '''
    p[0] = p[1]

def p_incr_command_12(p):
    '''incr_command : assembly '''
    p[0] = p[1]

def p_incr_command_13(p):
    '''incr_command : userdata '''
    p[0] = p[1]

def p_incr_command_14(p):
    '''incr_command : gui '''
    p[0] = p[1]

def p_incr_command_15(p):
    '''incr_command : SHADER symbol function_list '''
    # { mi_api_shader_add($2, $3); }

def p_code_bytes_list_1(p):
    '''code_bytes_list : T_BYTE_STRING '''
    # { mi_api_code_byte_copy($1.len, $1.bytes); }

def p_code_bytes_list_2(p):
    '''code_bytes_list : code_bytes_list T_BYTE_STRING '''
    # { mi_api_code_byte_copy($2.len, $2.bytes); }

def p_set_1(p):
    '''set : SET symbol '''
    # { mi_api_variable_set($2, 0); }

def p_set_2(p):
    '''set : SET symbol symbol '''
    # { mi_api_variable_set($2, $3); }

def p_call_1(p):
    '''call : CALL function_list '''
    # { mi_api_shader_call($2, 0, 0); }

def p_call_2(p):
    '''call : CALL function_list ',' symbol symbol '''
    # { mi_api_shader_call($2, $4, $5); }

def p_debug_1(p):
    '''debug : DEBUG symbol opt_symbol '''
    # { mi_api_debug($2, $3); }

def p_version_1(p):
    '''version : VERSION T_STRING '''
    # { mi_api_version_check($2, 0); }

def p_version_2(p):
    '''version : MIN VERSION T_STRING '''
    # { mi_api_version_check($3, 0); }

def p_version_3(p):
    '''version : MAX VERSION T_STRING '''
    # { mi_api_version_check($3, 1); }

def p_frame_1(p):
    '''frame : _embed0_frame frame_number initial_frame_cmd_list view frame_command_list END FRAME '''
    # { mi_timing(my_timer, "mi scene file parsing");
    #                           mi_timing(my_timer, 0);
    #                           mi_api_frame_end();
    #                           yyreturn MIYYENDFRAME; }

def p__embed0_frame(p):
    '''_embed0_frame : '''
    # { mi_api_frame_begin(&camera, &options); }

def p_initial_frame_cmd_list_1(p):
    '''initial_frame_cmd_list :  '''

def p_initial_frame_cmd_list_2(p):
    '''initial_frame_cmd_list : initial_frame_cmd_list initial_frame_cmd '''

def p_initial_frame_cmd_1(p):
    '''initial_frame_cmd : texture '''

def p_initial_frame_cmd_2(p):
    '''initial_frame_cmd : light '''

def p_initial_frame_cmd_3(p):
    '''initial_frame_cmd : material '''

def p_frame_command_list_1(p):
    '''frame_command_list :  '''

def p_frame_command_list_2(p):
    '''frame_command_list : frame_command_list frame_command '''

def p_frame_command_1(p):
    '''frame_command : texture '''

def p_frame_command_2(p):
    '''frame_command : light '''

def p_frame_command_3(p):
    '''frame_command : material '''

def p_frame_command_4(p):
    '''frame_command : object '''

def p_frame_command_5(p):
    '''frame_command : call '''

def p_frame_command_6(p):
    '''frame_command : debug '''

def p_frame_command_7(p):
    '''frame_command : version '''

def p_frame_command_8(p):
    '''frame_command : gui '''


#======================================
# ? : view
#======================================
#
# ???

def p_view_1(p):
    '''view : VIEW _embed0_view view_list END VIEW '''

def p__embed0_view(p):
    '''_embed0_view : '''
    # {
    #                             have_l = have_v = have_e = have_p = 0;
    #                             if (is_incremental == miFALSE) {
    #                                 mi_api_function_delete(&camera->output);
    #                                 Edit_fb fb(camera->buffertag);
    #                                 fb->reset();
    #                             }
    #                           }

def p_view_list_1(p):
    '''view_list :  '''

def p_view_list_2(p):
    '''view_list : view_list view_item '''

def p_view_item_1(p):
    '''view_item : camview_item '''

def p_view_item_2(p):
    '''view_item : optview_item '''

def p_view_item_3(p):
    '''view_item : MIN SAMPLES T_INTEGER '''
    # { options->min_samples = $3; }

def p_view_item_4(p):
    '''view_item : MAX SAMPLES T_INTEGER '''
    # { options->max_samples = $3; }

def p_view_item_5(p):
    '''view_item : SAMPLES T_INTEGER '''
    # { mi_api_warning(
    #                                 "\"samples\" view parameter ignored"); }

def p_view_item_6(p):
    '''view_item : RECURSIVE boolean '''
    # { if (!$2)
    #                                 mi_api_warning("\"recursive off\" ignored"); }

def p_view_item_7(p):
    '''view_item : ADAPTIVE boolean '''
    # { mi_api_warning("\"adaptive\" statement ignored"); }

def p_view_item_8(p):
    '''view_item : ACCELERATION RAY CLASSIFICATION '''
    # { options->acceleration = 'b';
    #                           mi_api_warning(
    #                                 "ray classification is obsolete, using BSP"); }

def p_view_item_9(p):
    '''view_item : ACCELERATION SPATIAL SUBDIVISION '''
    # { options->acceleration = 'b'; }

def p_view_item_10(p):
    '''view_item : ACCELERATION GRID '''
    # { options->acceleration = 'g'; }

def p_view_item_11(p):
    '''view_item : SUBDIVISION MEMORY T_INTEGER '''
    # { mi_api_warning("ray classification is obsolete, "
    #                           "statement \"subdivision memory %d\" ignored", $3); }

def p_view_item_12(p):
    '''view_item : SUBDIVISION T_INTEGER T_INTEGER '''
    # { mi_api_warning("ray classification is obsolete, "
    #                           "statement \"subdivision %d %d\" ignored", $2, $3); }

def p_view_item_13(p):
    '''view_item : MAX SIZE T_INTEGER '''
    # { options->space_max_size = $3; }

def p_view_item_14(p):
    '''view_item : MAX DEPTH T_INTEGER '''
    # { options->space_max_depth = $3; }

def p_view_item_15(p):
    '''view_item : SHADOW SORT boolean '''
    # { if ($3) options->shadow = 'l'; }

def p_view_item_16(p):
    '''view_item : SHADOW SEGMENTS boolean '''
    # { if ($3) options->shadow = 's'; }

def p_view_item_17(p):
    '''view_item : transform '''
    # { mi_api_view_transform($1); }

def p_view_item_18(p):
    '''view_item : RED floating floating '''

def p_view_item_19(p):
    '''view_item : GREEN floating floating '''

def p_view_item_20(p):
    '''view_item : BLUE floating floating '''

def p_view_item_21(p):
    '''view_item : WHITE floating floating '''


#======================================
# miOptions : options
#======================================
#
#    options "name"  
#        option_statements  
#    end options  

def p_options_1(p):
    '''options : OPTIONS symbol _embed0_options option_list END OPTIONS '''
    # { string_options->release();
    #                           string_options = 0;
    #                           mi_api_options_end(); }
    type = p[1]
    name = p[2]
    text = ''
    attrs = p[4]
    #p[0] = NamedEntity(type, text, name, attrs=attrs)
    
def p__embed0_options(p):
    '''_embed0_options : '''
    # {
    #                         options = mi_api_options_begin($2);
    #                         iface = mi_get_shader_interface();
    #                         string_options = iface->getOptions(options->string_options);
    #                         iface->release();
    #                         iface = 0;
    #                         have_pm = miFALSE; 
    #                         have_sf = 0;
    #                     }

def p_option_list_1(p):
    '''option_list :  '''
    p[0] = []
	
def p_option_list_2(p):
    '''option_list : option_list option_item '''
    p[0] = p[1] + [p[2]]
	
def p_option_item_1(p):
    '''option_item : optview_item '''
    p[0] = p[1]
    
def p_option_item_2(p):
    '''option_item : string_option_item '''
    p[0] = p[1]

def p_option_item_3(p):
    '''option_item : _embed0_option_item data '''

def p_option_item_4(p):
    '''option_item : ACCELERATION RAYCL '''
    # { options->acceleration = 'b';
    #                           mi_api_warning(
    #                                 "ray classification is obsolete, using BSP"); }


def p_option_item_5(p):
    '''option_item : ACCELERATION BSP '''
    # { options->acceleration = 'b'; }


def p_option_item_6(p):
    '''option_item : ACCELERATION BSP2 '''
    # { options->acceleration = 'n'; }


def p_option_item_7(p):
    '''option_item : ACCELERATION LARGE BSP '''
    # { options->acceleration = 'l'; }


def p_option_item_8(p):
    '''option_item : ACCELERATION GRID '''
    # { options->acceleration = 'g'; }


def p_option_item_9(p):
    '''option_item : MOTION boolean '''
    # { if ($2) options->motion = 1; }


def p_option_item_10(p):
    '''option_item : MOTION STEPS T_INTEGER '''
    # { options->n_motion_vectors = $3;}


def p_option_item_11(p):
    '''option_item : DIAGNOSTIC SAMPLES boolean '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_SAMPLES,$3);}


def p_option_item_12(p):
    '''option_item : DIAGNOSTIC PHOTON OFF '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_PHOTON, miFALSE);}


def p_option_item_13(p):
    '''option_item : DIAGNOSTIC PHOTON DENSITY floating '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_PHOTON, miFALSE);
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_PHOTON_D, miTRUE);
    #                           options->diag_photon_density = $4;}


def p_option_item_14(p):
    '''option_item : DIAGNOSTIC PHOTON IRRADIANCE floating '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_PHOTON, miFALSE);
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_PHOTON_I, miTRUE);
    #                           options->diag_photon_density = $4;}


def p_option_item_15(p):
    '''option_item : DIAGNOSTIC GRID OFF '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID, miFALSE);}


def p_option_item_16(p):
    '''option_item : DIAGNOSTIC GRID OBJECT floating '''
    # { options->diag_grid_size = $4;
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID, miFALSE);
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID_O, $4 != 0.0);}


def p_option_item_17(p):
    '''option_item : DIAGNOSTIC GRID WORLD floating '''
    # { options->diag_grid_size = $4;
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID, miFALSE);
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID_W, $4 != 0.0);}


def p_option_item_18(p):
    '''option_item : DIAGNOSTIC GRID CAMERA floating '''
    # { options->diag_grid_size = $4;
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID, miFALSE);
    #                           miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_GRID_C, $4 != 0.0);}


def p_option_item_19(p):
    '''option_item : DIAGNOSTIC BSP OFF '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_BSP, miFALSE); }


def p_option_item_20(p):
    '''option_item : DIAGNOSTIC BSP DEPTH '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_BSP_D, miTRUE); }


def p_option_item_21(p):
    '''option_item : DIAGNOSTIC BSP SIZE '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_BSP_L, miTRUE); }


def p_option_item_22(p):
    '''option_item : DIAGNOSTIC FINALGATHER boolean '''
    # { miBIT_SWITCH(options->diagnostic_mode,
    #                                 miSCENE_DIAG_FG, $3);}


def p_option_item_23(p):
    '''option_item : DIAGNOSTIC HARDWARE boolean '''
    # { miBIT_SWITCH(options->hardware_diagnostic,
    #                                 miSCENE_HWDIAG_SOLID, $3); }

def p_option_item_24(p):
    '''option_item : DIAGNOSTIC HARDWARE GRID '''
    # { miBIT_SWITCH(options->hardware_diagnostic,
    #                                 miSCENE_HWDIAG_WIRE, miTRUE); }


def p_option_item_25(p):
    '''option_item : DIAGNOSTIC HARDWARE WINDOW '''
    # { miBIT_SWITCH(options->hardware_diagnostic,
    #                                         miSCENE_HWDIAG_WINDOW, miTRUE); }


def p_option_item_26(p):
    '''option_item : DIAGNOSTIC HARDWARE LIGHT '''
    # { miBIT_SWITCH(options->hardware_diagnostic,
    #                                 miSCENE_HWDIAG_LIGHTS, miTRUE); }

def p_option_item_27(p):
    '''option_item : SAMPLES T_INTEGER '''
    # { options->min_samples = $2-2;
    #                           options->max_samples = $2; }

def p_option_item_28(p):
    '''option_item : SAMPLES T_INTEGER T_INTEGER '''
    # { options->min_samples = $2;
    #                           options->max_samples = $3; }

def p_option_item_29(p):
    '''option_item : SAMPLES T_INTEGER T_INTEGER T_INTEGER T_INTEGER '''
    # { options->min_samples = $2;
    #                           options->max_samples = $3;
    #                           options->def_min_samples = $4;
    #                           options->def_max_samples = $5; }

def p_option_item_30(p):
    '''option_item : SAMPLES COLLECT T_INTEGER '''
    # { if ($3 > 0)
    #                                 options->rast_collect_rate = $3;
    #                           else if ($3 < 0)
    #                                 mi_warning("invalid negative \"samples"
    #                                            " collect %d\" has been ignored.",
    #                                            $3);
    #                         }

def p_option_item_31(p):
    '''option_item : SAMPLES MOTION T_INTEGER '''
    # { options->rast_motion_resample = $3; }

def p_option_item_32(p):
    '''option_item : SHADOW SORT '''
    # { options->shadow = 'l'; }

def p_option_item_33(p):
    '''option_item : SHADOW SEGMENTS '''
    # { options->shadow = 's'; }

def p_option_item_34(p):
    '''option_item : COLORPROFILE symbol '''
    # { options->render_cprof = mi_api_name_lookup($2); }

def p_option_item_35(p):
    '''option_item : options_attribute '''

def p__embed0_option_item(p):
    '''_embed0_option_item : '''
    # { curr_datatag = &options->userdata; }

def p_optview_item_1(p):
    '''optview_item : SHADOW OFF '''
    # { options->shadow = 0; }

def p_optview_item_2(p):
    '''optview_item : SHADOW ON '''
    # { options->shadow = 1; }

def p_optview_item_3(p):
    '''optview_item : TRACE boolean '''
    # { options->trace = $2; }

def p_optview_item_4(p):
    '''optview_item : SCANLINE boolean '''
    # { options->scanline = $2; }

def p_optview_item_5(p):
    '''optview_item : SCANLINE RAST '''
    # { options->scanline = 'r'; }

def p_optview_item_6(p):
    '''optview_item : SCANLINE RAPID '''
    # { options->scanline = 'r'; }

def p_optview_item_7(p):
    '''optview_item : SCANLINE OPENGL '''
    # { options->scanline = 'o'; }

def p_optview_item_8(p):
    '''optview_item : HARDWARE boolean '''
    # { options->hardware = $2 ? 1 : 0; }

def p_optview_item_9(p):
    '''optview_item : HARDWARE ALL '''
    # { options->hardware = 3; }

def p_optview_item_10(p):
    '''optview_item : HARDWARE FORCE '''
    # { options->hwshader |= 1; }

def p_optview_item_11(p):
    '''optview_item : HARDWARE CG '''
    # { options->hwshader |= 2; }

def p_optview_item_12(p):
    '''optview_item : HARDWARE NATIVE '''
    # { options->hwshader |= 4; }

def p_optview_item_13(p):
    '''optview_item : HARDWARE FAST '''
    # { options->hwshader |= 8; }

def p_optview_item_14(p):
    '''optview_item : HARDWARE SAMPLES T_INTEGER T_INTEGER '''
    # { hoptions = mi_rchw_get_options(); 
    #                           hoptions->multi_samples = $3;
    #                           hoptions->super_samples = $4; }

def p_optview_item_15(p):
    '''optview_item : LENS boolean '''
    # { options->no_lens = !$2; }

def p_optview_item_16(p):
    '''optview_item : VOLUME boolean '''
    # { options->no_volume = !$2; }

def p_optview_item_17(p):
    '''optview_item : GEOMETRY boolean '''
    # { options->no_geometry = !$2; }

def p_optview_item_18(p):
    '''optview_item : DISPLACE boolean '''
    # { options->no_displace = !$2; }

def p_optview_item_19(p):
    '''optview_item : DISPLACE PRESAMPLE boolean '''
    # { options->no_predisplace = !$3; }

def p_optview_item_20(p):
    '''optview_item : OUTPUT boolean '''
    # { options->no_output = !$2; }

def p_optview_item_21(p):
    '''optview_item : MERGE boolean '''
    # { options->no_merge = !$2; }

def p_optview_item_22(p):
    '''optview_item : HAIR boolean '''
    # { options->no_hair = !$2; }

def p_optview_item_23(p):
    '''optview_item : PASS boolean '''
    # { options->no_pass = !$2; }

def p_optview_item_24(p):
    '''optview_item : AUTOVOLUME boolean '''
    # { options->autovolume = $2; }

def p_optview_item_25(p):
    '''optview_item : PHOTON AUTOVOLUME boolean '''
    # { options->photon_autovolume = $3; }

def p_optview_item_26(p):
    '''optview_item : FILTER filter_type '''
    # { options->filter     = $2;
    #                           options->filter_size_x =
    #                           options->filter_size_y = 0.0; }

def p_optview_item_27(p):
    '''optview_item : FILTER filter_type floating '''
    # { options->filter     = $2;
    #                           options->filter_size_x =
    #                           options->filter_size_y = $3; }

def p_optview_item_28(p):
    '''optview_item : FILTER filter_type floating floating '''
    # { options->filter     = $2;
    #                           options->filter_size_x = $3;
    #                           options->filter_size_y = $4; }

def p_optview_item_29(p):
    '''optview_item : FACE FRONT '''
    # { options->face = 'f'; }

def p_optview_item_30(p):
    '''optview_item : FACE BACK '''
    # { options->face = 'b'; }

def p_optview_item_31(p):
    '''optview_item : FACE BOTH '''
    # { options->face = 'a'; }

def p_optview_item_32(p):
    '''optview_item : FIELD OFF '''
    # { options->field = 0; }

def p_optview_item_33(p):
    '''optview_item : FIELD EVEN '''
    # { options->field = 'e'; }

def p_optview_item_34(p):
    '''optview_item : FIELD ODD '''
    # { options->field = 'o'; }

def p_optview_item_35(p):
    '''optview_item : SAMPLELOCK boolean '''
    # { options->samplelock = $2; }

def p_optview_item_36(p):
    '''optview_item : PHOTON TRACE DEPTH T_INTEGER '''
    # { options->photon_reflection_depth = $4;
    #                           options->photon_refraction_depth = $4;
    #                           options->photon_trace_depth           = $4 + $4; }

def p_optview_item_37(p):
    '''optview_item : PHOTON TRACE DEPTH T_INTEGER T_INTEGER '''
    # { options->photon_reflection_depth = $4;
    #                           options->photon_refraction_depth = $5;
    #                           options->photon_trace_depth           = $4 + $5; }

def p_optview_item_38(p):
    '''optview_item : PHOTON TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER '''
    # { options->photon_reflection_depth = $4;
    #                           options->photon_refraction_depth = $5;
    #                           options->photon_trace_depth           = $6; }

def p_optview_item_39(p):
    '''optview_item : FINALGATHER TRACE DEPTH T_INTEGER '''
    # { options->fg_reflection_depth =
    #                           options->fg_refraction_depth = $4;
    #                           options->fg_diffuse_depth    =
    #                           options->fg_trace_depth      = $4 + $4; }

def p_optview_item_40(p):
    '''optview_item : FINALGATHER TRACE DEPTH T_INTEGER T_INTEGER '''
    # { options->fg_reflection_depth = $4;
    #                           options->fg_refraction_depth = $5;
    #                           options->fg_diffuse_depth    =
    #                           options->fg_trace_depth      = $4 + $5; }

def p_optview_item_41(p):
    '''optview_item : FINALGATHER TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER '''
    # { options->fg_reflection_depth = $4;
    #                           options->fg_refraction_depth = $5;
    #                           options->fg_diffuse_depth    =
    #                           options->fg_trace_depth      = $6; }

def p_optview_item_42(p):
    '''optview_item : FINALGATHER TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER T_INTEGER '''
    # { options->fg_reflection_depth = $4;
    #                           options->fg_refraction_depth = $5;
    #                           options->fg_diffuse_depth    = $6; 
    #                           options->fg_trace_depth      = $7; }

def p_optview_item_43(p):
    '''optview_item : TRACE DEPTH T_INTEGER '''
    # { options->reflection_depth = $3;
    #                           options->refraction_depth = $3;
    #                           options->trace_depth           = $3 + $3; }

def p_optview_item_44(p):
    '''optview_item : TRACE DEPTH T_INTEGER T_INTEGER '''
    # { options->reflection_depth = $3;
    #                           options->refraction_depth = $4;
    #                           options->trace_depth           = $3 + $4; }

def p_optview_item_45(p):
    '''optview_item : TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER '''
    # { options->reflection_depth  = $3;
    #                           options->refraction_depth  = $4;
    #                           options->trace_depth       = $5; }

def p_optview_item_46(p):
    '''optview_item : CONTRAST floating floating floating '''
    # { options->contrast.r = $2;
    #                           options->contrast.g = $3;
    #                           options->contrast.b = $4;
    #                           options->contrast.a = ($2 + $3 + $4)/3; }

def p_optview_item_47(p):
    '''optview_item : CONTRAST floating floating floating floating '''
    # { options->contrast.r = $2;
    #                           options->contrast.g = $3;
    #                           options->contrast.b = $4;
    #                           options->contrast.a = $5; }

def p_optview_item_48(p):
    '''optview_item : TIME CONTRAST floating floating floating '''
    # { options->time_contrast.r = $3;
    #                           options->time_contrast.g = $4;
    #                           options->time_contrast.b = $5;
    #                           options->time_contrast.a = ($3 + $4 + $5)/3; }

def p_optview_item_49(p):
    '''optview_item : TIME CONTRAST floating floating floating floating '''
    # { options->time_contrast.r = $3;
    #                           options->time_contrast.g = $4;
    #                           options->time_contrast.b = $5;
    #                           options->time_contrast.a = $6; }

def p_optview_item_50(p):
    '''optview_item : CONTOUR STORE function '''
    # { options->contour_store = $3; }

def p_optview_item_51(p):
    '''optview_item : CONTOUR CONTRAST function '''
    # { options->contour_contrast = $3; }

def p_optview_item_52(p):
    '''optview_item : STATE function '''
    # {
    #                             if (!have_sf++)
    #                                 mi_api_function_delete(&options->state_func);
    #                             options->state_func = mi_api_function_append(options->state_func, $2);
    #                         }

def p_optview_item_53(p):
    '''optview_item : STATE function_array '''
    # {
    #                             if ($2 != miNULLTAG) {
    #                                 if (!have_sf++)
    #                                     mi_api_function_delete(&options->state_func);
    #                                 options->state_func = mi_api_function_append(
    #                                                                 options->state_func, $2);
    #                             } else {
    #                                 mi_api_function_delete(&options->state_func);
    #                                 have_sf = 0;
    #                             }
    #                         }

def p_optview_item_54(p):
    '''optview_item : JITTER floating '''
    # { options->jitter     = $2; }

def p_optview_item_55(p):
    '''optview_item : SHUTTER floating '''
    # { options->shutter    = $2;
    #                           options->motion     = options->shutter > 0; }

def p_optview_item_56(p):
    '''optview_item : SHUTTER floating floating '''
    # { options->shutter_delay = $2;
    #                           options->shutter    = $3;
    #                           options->motion     = options->shutter > 0; }

def p_optview_item_57(p):
    '''optview_item : TASK SIZE T_INTEGER '''
    # { options->task_size = $3; }

def p_optview_item_58(p):
    '''optview_item : RAYCL SUBDIVISION T_INTEGER T_INTEGER '''
    # { mi_api_warning("ray classification is obsolete, "
    #                           "statement \"raycl subdivision %d %d\" ignored",
    #                                                                 $3, $4); }

def p_optview_item_59(p):
    '''optview_item : RAYCL MEMORY T_INTEGER '''
    # { mi_api_warning("ray classification is obsolete, "
    #                           "statement \"raycl memory %d\" ignored", $3); }

def p_optview_item_60(p):
    '''optview_item : BSP SIZE T_INTEGER '''
    # { options->space_max_size = $3; }

def p_optview_item_61(p):
    '''optview_item : BSP DEPTH T_INTEGER '''
    # { options->space_max_depth = $3; }

def p_optview_item_62(p):
    '''optview_item : BSP MEMORY T_INTEGER '''
    # { options->space_max_mem = $3; }

def p_optview_item_63(p):
    '''optview_item : BSP SHADOW boolean '''
    # { options->space_shadow_separate = $3; }

def p_optview_item_64(p):
    '''optview_item : GRID SIZE T_INTEGER '''
    # { options->grid_max_size = $3; }

def p_optview_item_65(p):
    '''optview_item : GRID SIZE T_FLOAT '''
    # { options->grid_res[0] =
    #                           options->grid_res[1] =
    #                           options->grid_res[2] = (int)$3;
    #                           mi_api_warning("obsolete grid size statement, "
    #                                 "use grid resolution instead"); }

def p_optview_item_66(p):
    '''optview_item : GRID RESOLUTION T_INTEGER '''
    # { options->grid_res[0] =
    #                           options->grid_res[1] =
    #                           options->grid_res[2] = $3; }

def p_optview_item_67(p):
    '''optview_item : GRID RESOLUTION T_INTEGER T_INTEGER T_INTEGER '''
    # { options->grid_res[0] = $3;
    #                           options->grid_res[1] = $4;
    #                           options->grid_res[2] = $5; }

def p_optview_item_68(p):
    '''optview_item : GRID DEPTH T_INTEGER '''
    # { options->grid_max_depth = $3; }

def p_optview_item_69(p):
    '''optview_item : DESATURATE boolean '''
    # { options->desaturate = $2; }

def p_optview_item_70(p):
    '''optview_item : DITHER boolean '''
    # { options->dither = $2; }

def p_optview_item_71(p):
    '''optview_item : PREMULTIPLY boolean '''
    # { options->nopremult = !$2; }

def p_optview_item_72(p):
    '''optview_item : COLORCLIP colorclip_mode '''
    # { options->colorclip = $2; }

def p_optview_item_73(p):
    '''optview_item : GAMMA floating '''
    # { options->gamma = $2; }

def p_optview_item_74(p):
    '''optview_item : OBJECT SPACE '''
    # { options->render_space = 'o'; }

def p_optview_item_75(p):
    '''optview_item : CAMERA SPACE '''
    # { options->render_space = 'c'; }

def p_optview_item_76(p):
    '''optview_item : MIXED SPACE '''
    # { options->render_space = 'm'; }

def p_optview_item_77(p):
    '''optview_item : WORLD SPACE '''
    # { mi_api_warning(
    #                                 "world space statement ignored"); }

def p_optview_item_78(p):
    '''optview_item : INHERITANCE symbol '''
    # { options->inh_is_traversal = miFALSE;
    #                           if (ctx->inheritance_func)
    #                                 mi_api_release(ctx->inheritance_func);
    #                           ctx->inheritance_func = $2;
    #                           if (!(options->inh_funcdecl = mi_api_decl_lookup(
    #                                                            mi_api_strdup($2))))
    #                                 mi_api_nerror(176, "undeclared inheritance "
    #                                                           "shader \"%s\"", $2);
    #                         }

def p_optview_item_79(p):
    '''optview_item : TRAVERSAL symbol '''
    # { options->inh_is_traversal = miTRUE;
    #                           if (ctx->inheritance_func)
    #                                 mi_api_release(ctx->inheritance_func);
    #                           ctx->inheritance_func = $2;
    #                           if (!(options->inh_funcdecl = mi_api_decl_lookup(
    #                                                            mi_api_strdup($2))))
    #                                 mi_api_nerror(177, "undeclared traversal "
    #                                                           "shader \"%s\"", $2);
    #                         }

def p_optview_item_80(p):
    '''optview_item : SHADING SAMPLES floating '''
    # { options->rast_shading_samples = $3; }

def p_optview_item_81(p):
    '''optview_item : SHADOWMAP MOTION boolean '''
    # { options->shadow_map_motion = $3; }

def p_optview_item_82(p):
    '''optview_item : SHADOWMAP REBUILD boolean '''
    # { options->recompute_shadow_maps = (($3)?'y':'n');
    #                           options->shadowmap_flags &= ~miSHADOWMAP_MERGE; }

def p_optview_item_83(p):
    '''optview_item : SHADOWMAP REBUILD MERGE '''
    # { options->recompute_shadow_maps = 'm';
    #                           options->shadowmap_flags |= miSHADOWMAP_MERGE; }

def p_optview_item_84(p):
    '''optview_item : SHADOWMAP boolean '''
    # { options->use_shadow_maps &= 0x80;
    #                           options->shadowmap_flags &= ~miSHADOWMAP_DETAIL;
    #                           if ($2) options->use_shadow_maps |= 1;
    #                           else    options->use_shadow_maps  = 0; }

def p_optview_item_85(p):
    '''optview_item : SHADOWMAP OPENGL '''
    # { options->use_shadow_maps &= 0x80;
    #                           options->use_shadow_maps |= 'o'; }

def p_optview_item_86(p):
    '''optview_item : SHADOWMAP TRACE '''
    # { options->shadowmap_flags |= miSHADOWMAP_TRACE; }

def p_optview_item_87(p):
    '''optview_item : SHADOWMAP TRACE boolean '''
    # { if ($3)
    #                                 options->shadowmap_flags |= miSHADOWMAP_TRACE;
    #                           else
    #                                 options->shadowmap_flags &=~miSHADOWMAP_TRACE;}

def p_optview_item_88(p):
    '''optview_item : SHADOWMAP WINDOW '''
    # { options->shadowmap_flags |= miSHADOWMAP_CROP; }

def p_optview_item_89(p):
    '''optview_item : SHADOWMAP WINDOW boolean '''
    # { if ($3)
    #                                 options->shadowmap_flags |= miSHADOWMAP_CROP;
    #                           else
    #                                 options->shadowmap_flags &= ~miSHADOWMAP_CROP;}

def p_optview_item_90(p):
    '''optview_item : SHADOWMAP ONLY '''
    # { options->use_shadow_maps |= 0x80;
    #                           options->shadowmap_flags |= miSHADOWMAP_ONLY; }

def p_optview_item_91(p):
    '''optview_item : SHADOWMAP DETAIL '''
    # { options->use_shadow_maps &= 0x80;
    #                           options->use_shadow_maps |= 'd';
    #                           options->shadowmap_flags |= miSHADOWMAP_DETAIL; }

def p_optview_item_92(p):
    '''optview_item : SHADOWMAP BIAS floating '''
    # { options->shadowmap_bias = $3; }

def p_optview_item_93(p):
    '''optview_item : LIGHTMAP boolean '''
    # { options->lightmap = $2 ? miLIGHTMAP_ON 
    #                                                  : miLIGHTMAP_OFF; }

def p_optview_item_94(p):
    '''optview_item : LIGHTMAP ONLY '''
    # { options->lightmap = miLIGHTMAP_ONLY; }

def p_optview_item_95(p):
    '''optview_item : CAUSTIC boolean '''
    # { options->caustic = $2; }

def p_optview_item_96(p):
    '''optview_item : CAUSTIC T_INTEGER '''
    # { options->caustic_flag = $2; }

def p_optview_item_97(p):
    '''optview_item : CAUSTIC ACCURACY T_INTEGER '''
    # { options->caustic_accuracy = $3; }

def p_optview_item_98(p):
    '''optview_item : CAUSTIC ACCURACY T_INTEGER floating '''
    # { options->caustic_accuracy = $3;
    #                           options->caustic_radius = $4; }

def p_optview_item_99(p):
    '''optview_item : CAUSTIC FILTER c_filter_type '''
    # { options->caustic_filter = $3;
    #                           options->caustic_filter_const = 1.1; }

def p_optview_item_100(p):
    '''optview_item : CAUSTIC FILTER c_filter_type floating '''
    # { options->caustic_filter = $3;
    #                           options->caustic_filter_const = $4; }

def p_optview_item_101(p):
    '''optview_item : CAUSTIC SCALE color '''
    # { options->caustic_scale = $3; }

def p_optview_item_102(p):
    '''optview_item : GLOBILLUM boolean '''
    # { options->globillum = $2; }

def p_optview_item_103(p):
    '''optview_item : GLOBILLUM T_INTEGER '''
    # { options->globillum_flag = $2; }

def p_optview_item_104(p):
    '''optview_item : GLOBILLUM ACCURACY T_INTEGER '''
    # { options->globillum_accuracy = $3; }

def p_optview_item_105(p):
    '''optview_item : GLOBILLUM ACCURACY T_INTEGER floating '''
    # { options->globillum_accuracy = $3;
    #                           options->globillum_radius = $4; }

def p_optview_item_106(p):
    '''optview_item : GLOBILLUM SCALE color '''
    # { options->globillum_scale = $3; }

def p_optview_item_107(p):
    '''optview_item : FINALGATHER boolean '''
    # { options->finalgather = $2; }

def p_optview_item_108(p):
    '''optview_item : FINALGATHER FASTLOOKUP '''
    # { options->finalgather = 'f'; }

def p_optview_item_109(p):
    '''optview_item : FINALGATHER ONLY '''
    # { options->finalgather = 'o'; }

def p_optview_item_110(p):
    '''optview_item : FINALGATHER ACCURACY T_INTEGER '''
    # { options->finalgather_view      = miFALSE;
    #                           options->finalgather_rays      = $3; }

def p_optview_item_111(p):
    '''optview_item : FINALGATHER ACCURACY T_INTEGER floating '''
    # { options->finalgather_view      = miFALSE;
    #                           options->finalgather_rays      = $3;
    #                           options->finalgather_maxradius = $4;
    #                           options->finalgather_minradius = 0.0; }

def p_optview_item_112(p):
    '''optview_item : FINALGATHER ACCURACY T_INTEGER floating floating '''
    # { options->finalgather_view      = miFALSE;
    #                           options->finalgather_rays      = $3;
    #                           options->finalgather_maxradius = $4;
    #                           options->finalgather_minradius = $5; }

def p_optview_item_113(p):
    '''optview_item : FINALGATHER ACCURACY VIEW T_INTEGER '''
    # { options->finalgather_view      = miTRUE;
    #                           options->finalgather_rays      = $4; }

def p_optview_item_114(p):
    '''optview_item : FINALGATHER ACCURACY VIEW T_INTEGER floating '''
    # { options->finalgather_view      = miTRUE;
    #                           options->finalgather_rays      = $4;
    #                           options->finalgather_maxradius = $5;
    #                           options->finalgather_minradius = 0.0; }

def p_optview_item_115(p):
    '''optview_item : FINALGATHER ACCURACY VIEW T_INTEGER floating floating '''
    # { options->finalgather_view      = miTRUE;
    #                           options->finalgather_rays      = $4;
    #                           options->finalgather_maxradius = $5;
    #                           options->finalgather_minradius = $6; }

def p_optview_item_116(p):
    '''optview_item : FINALGATHER FILE map_list '''
    # { mi_api_taglist_reset(&options->finalgather_file,
    #                                          $3); }

def p_optview_item_117(p):
    '''optview_item : FINALGATHER FILTER T_INTEGER '''
    # { options->finalgather_filter  = $3; }

def p_optview_item_118(p):
    '''optview_item : FINALGATHER REBUILD boolean '''
    # { options->finalgather_rebuild = $3; }

def p_optview_item_119(p):
    '''optview_item : FINALGATHER REBUILD FREEZE '''
    # { options->finalgather_rebuild = 2; }

def p_optview_item_120(p):
    '''optview_item : FINALGATHER FALLOFF floating floating '''
    # { options->fg_falloff_start    = $3;
    #                           options->fg_falloff_stop     = $4; }

def p_optview_item_121(p):
    '''optview_item : FINALGATHER FALLOFF floating '''
    # { options->fg_falloff_start    = $3;
    #                           options->fg_falloff_stop     = $3; }

def p_optview_item_122(p):
    '''optview_item : FINALGATHER SCALE color '''
    # { options->finalgather_scale = $3; }

def p_optview_item_123(p):
    '''optview_item : FINALGATHER SECONDARY SCALE color '''
    # { options->finalgather_sec_scale = $4; }

def p_optview_item_124(p):
    '''optview_item : FINALGATHER PRESAMPLE DENSITY floating '''
    # { options->fg_presamp_density = $4; }

def p_optview_item_125(p):
    '''optview_item : PHOTONVOL ACCURACY T_INTEGER '''
    # { options->photonvol_accuracy  = $3; }

def p_optview_item_126(p):
    '''optview_item : PHOTONVOL ACCURACY T_INTEGER floating '''
    # { options->photonvol_accuracy  = $3;
    #                           options->photonvol_radius    = $4; }

def p_optview_item_127(p):
    '''optview_item : PHOTONVOL SCALE color '''
    # { options->photonvol_scale = $3; }

def p_optview_item_128(p):
    '''optview_item : PHOTONMAP FILE '''
    # { mi_scene_delete(options->photonmap_file);
    #                           options->photonmap_file = 0; }

def p_optview_item_129(p):
    '''optview_item : PHOTONMAP FILE OFF '''
    # { mi_scene_delete(options->photonmap_file);
    #                           options->photonmap_file = 0; }

def p_optview_item_130(p):
    '''optview_item : PHOTONMAP FILE T_STRING '''
    # { mi_scene_delete(options->photonmap_file);
    #                           if (($3)[0]) {
    #                               strcpy((char *)mi_scene_create(
    #                                             &options->photonmap_file,
    #                                             miSCENE_STRING, strlen($3)+1), $3);
    #                               mi_scene_edit_end(options->photonmap_file);
    #                           } else {
    #                               options->photonmap_file = 0;
    #                           }
    #                           mi_api_release($3);
    #                         }

def p_optview_item_131(p):
    '''optview_item : PHOTONMAP ONLY '''
    # { options->photonmap_only = miTRUE; }

def p_optview_item_132(p):
    '''optview_item : PHOTONMAP ONLY boolean '''
    # { options->photonmap_only = $3; }

def p_optview_item_133(p):
    '''optview_item : PHOTONMAP REBUILD boolean '''
    # { options->photonmap_rebuild = $3; }

def p_optview_item_134(p):
    '''optview_item : APPROXIMATE opt_displace '''

def p_optview_item_135(p):
    '''optview_item : FRAME BUFFER T_INTEGER opt_symbol '''
    # { mi_api_framebuffer(options, $3, $4); }

def p_optview_item_136(p):
    '''optview_item : LUMINANCE WEIGHT NTSC '''
    # { options->luminance_weight.r = 0.299;
    #                           options->luminance_weight.g = 0.587;
    #                           options->luminance_weight.b = 0.114;
    #                           options->luminance_weight.a = 0.0; }

def p_optview_item_137(p):
    '''optview_item : LUMINANCE WEIGHT color '''
    # { options->luminance_weight = $3; }

def p_optview_item_138(p):
    '''optview_item : MAX DISPLACE floating '''
    # { options->maxdisplace = $3; }

def p_map_list_1(p):
    '''map_list : '[' _embed0_map_list map_list_items ']' '''
    # { $$ = taglist; }

def p_map_list_2(p):
    '''map_list : T_STRING '''
    # { if (($1)[0]) {
    #                                 taglist = mi_api_dlist_create(miDLIST_TAG);
    #                                 strcpy((char *)mi_scene_create(
    #                                       &tag, miSCENE_STRING, strlen($1)+1), $1);
    #                                 mi_scene_edit_end(tag);
    #                                 mi_api_release($1);
    #                                 mi_api_dlist_add(taglist, (void *)(miIntptr)tag);
    #                                 $$ = taglist;
    #                             } else {
    #                                 mi_api_release($1);
    #                                 $$ = NULL;
    #                             } 
    #                           }

def p_map_list_3(p):
    '''map_list : OFF '''
    # { $$ = NULL; }

def p_map_list_4(p):
    '''map_list :  '''
    # { $$ = NULL; }

def p__embed0_map_list(p):
    '''_embed0_map_list : '''
    # { taglist = mi_api_dlist_create(miDLIST_TAG); }

def p_map_list_items_1(p):
    '''map_list_items : T_STRING _embed0_map_list_items map_list_next '''

def p__embed0_map_list_items(p):
    '''_embed0_map_list_items : '''
    # { strcpy((char *)mi_scene_create(
    #                                 &tag, miSCENE_STRING, strlen($1)+1), $1);
    #                           mi_scene_edit_end(tag);
    #                           mi_api_release($1);
    #                           mi_api_dlist_add(taglist, (void *)(miIntptr)tag); }

def p_map_list_next_1(p):
    '''map_list_next :  '''

def p_map_list_next_2(p):
    '''map_list_next : ',' '''

def p_map_list_next_3(p):
    '''map_list_next : ',' map_list_items '''

def p_filter_type_1(p):
    '''filter_type : BOX '''
    # { $$ = 'b'; }

def p_filter_type_2(p):
    '''filter_type : TRIANGLE '''
    # { $$ = 't'; }

def p_filter_type_3(p):
    '''filter_type : GAUSS '''
    # { $$ = 'g'; }

def p_filter_type_4(p):
    '''filter_type : MITCHELL '''
    # { $$ = 'm'; }

def p_filter_type_5(p):
    '''filter_type : LANCZOS '''
    # { $$ = 'l'; }

def p_filter_type_6(p):
    '''filter_type : CLIP MITCHELL '''
    # { $$ = 'M'; }

def p_filter_type_7(p):
    '''filter_type : CLIP LANCZOS '''
    # { $$ = 'c'; }

def p_c_filter_type_1(p):
    '''c_filter_type : BOX '''
    # { $$ = 'b'; }

def p_c_filter_type_2(p):
    '''c_filter_type : CONE '''
    # { $$ = 'c'; }

def p_c_filter_type_3(p):
    '''c_filter_type : GAUSS '''
    # { $$ = 'g'; }

def p_opt_displace_1(p):
    '''opt_displace : _embed0_opt_displace s_approx_tech ALL '''
    # { memcpy(&options->approx, &approx, sizeof(miApprox));}

def p_opt_displace_2(p):
    '''opt_displace : _embed1_opt_displace DISPLACE s_approx_tech ALL '''
    # { memcpy(&options->approx_displace, &approx,
    #                                                            sizeof(miApprox)); }

def p__embed0_opt_displace(p):
    '''_embed0_opt_displace : '''
    # { miAPPROX_DEFAULT(approx); }

def p__embed1_opt_displace(p):
    '''_embed1_opt_displace : '''
    # { miAPPROX_DEFAULT(approx); }

def p_string_option_item_1(p):
    '''string_option_item : T_STRING boolean '''
    # { string_options->set($1, $2 != 0); 
    #                           mi_api_release($1); }

def p_string_option_item_2(p):
    '''string_option_item : T_STRING T_STRING '''
    # { string_options->set($1, $2);
    #                           mi_api_release($1);
    #                           mi_api_release($2); }
    
def p_string_option_item_3(p):
    '''string_option_item : T_STRING T_INTEGER '''
    # { string_options->set($1, $2);
    #                           mi_api_release($1); }

def p_string_option_item_4(p):
    '''string_option_item : T_STRING T_FLOAT '''
    # { string_options->set($1, (float)$2);
    #                           mi_api_release($1); }

def p_string_option_item_5(p):
    '''string_option_item : T_STRING floating floating floating '''
    # { string_options->set($1, (float)$2, (float)$3, (float)$4); 
    #                           mi_api_release($1); }

def p_string_option_item_6(p):
    '''string_option_item : T_STRING floating floating floating floating '''
    # { string_options->set($1, (float)$2, (float)$3, (float)$4, (float)$5);
    #                           mi_api_release($1); }

#======================================
# miCamera : camera
#======================================
#
#    camera "name"
#        [framebuffer_statements]
#        [output_statements]
#        [pass_statements]
#        [camera_statements]
#    end camera  

def p_camera_1(p):
    '''camera : CAMERA symbol _embed0_camera camera_list END CAMERA '''
    # { mi_api_camera_end(); }

def p__embed0_camera(p):
    '''_embed0_camera : '''
    # {
    #                         camera = mi_api_camera_begin($2);
    #                         have_l = have_v = have_e = have_p = 0;
    #                         if (is_incremental == miFALSE)
    #                             mi_api_function_delete(&camera->output);
    #                     }

def p_camera_list_1(p):
    '''camera_list :  '''

def p_camera_list_2(p):
    '''camera_list : camera_list camera_item '''

def p_camera_item_1(p):
    '''camera_item : camview_item '''

def p_camera_item_2(p):
    '''camera_item : frame_number '''

def p_camera_item_3(p):
    '''camera_item : FIELD T_INTEGER '''
    # { camera->frame_field = $2; }

def p_camera_item_4(p):
    '''camera_item : dummy_attribute '''

def p_camview_item_1(p):
    '''camview_item : OUTPUT '''
    # {
    #                         Edit_fb fb(camera->buffertag);
    #                         fb->reset();
    #                         mi_api_function_delete(&camera->output);
    #                     }

def p_camview_item_2(p):
    '''camview_item : OUTPUT colorspace_set T_STRING T_STRING '''
    # {
    #                         mi_api_output_colorprofile($2);
    #                         mi_api_framebuffer_add(camera->buffertag, 0, $3, 0, $4);
    #                     }

def p_camview_item_3(p):
    '''camview_item : OUTPUT colorspace_set T_STRING out_parms T_STRING '''
    # {
    #                         mi_api_output_colorprofile($2);
    #                         mi_api_framebuffer_add(camera->buffertag, 0, $3, $4, $5);
    #                     }

def p_camview_item_4(p):
    '''camview_item : OUTPUT colorspace_set T_STRING T_STRING T_STRING '''
    # {
    #                         mi_api_output_colorprofile($2);
    #                         mi_api_framebuffer_add(camera->buffertag, $3, $4, 0, $5);
    #                     }

def p_camview_item_5(p):
    '''camview_item : OUTPUT colorspace_set T_STRING T_STRING out_parms T_STRING '''
    # {
    #                         mi_api_output_colorprofile($2);
    #                         mi_api_framebuffer_add(camera->buffertag, $3, $4, $5, $6);
    #                     }

def p_camview_item_6(p):
    '''camview_item : OUTPUT colorspace_set function '''
    # {
    #                         mi_api_output_colorprofile($2);
    #                         camera->output = mi_api_function_append(
    #                             camera->output, mi_api_output_function_def(0, 0, $3));
    #                     }

def p_camview_item_7(p):
    '''camview_item : OUTPUT colorspace_set T_STRING function '''
    # {
    #                         mi_api_output_colorprofile($2);
    #                         mi_api_output_type_identify(&tbm, &ibm, $3);
    #                         camera->output = mi_api_function_append(
    #                             camera->output, mi_api_output_function_def(tbm, ibm, $4));
    #                     }

def p_camview_item_8(p):
    '''camview_item : PASS NULL '''
    # { mi_api_function_delete(&camera->pass); }

def p_camview_item_9(p):
    '''camview_item : PASS pass_samples opt_string WRITE T_STRING '''
    # { if (!have_p++)
    #                                 mi_api_function_delete(&camera->pass);
    #                           mi_api_output_type_identify(&tbm, &ibm, $3);
    #                           camera->pass = mi_api_function_append(camera->pass,
    #                                 mi_api_pass_save_def(tbm, ibm, $2, $5)); }

def p_camview_item_10(p):
    '''camview_item : PASS PREP pass_samples opt_string READ T_STRING WRITE T_STRING function_list '''
    # { if (!have_p++)
    #                                 mi_api_function_delete(&camera->pass);
    #                           mi_api_output_type_identify(&tbm, &ibm, $4);
    #                           camera->pass = mi_api_function_append(camera->pass,
    #                                 mi_api_pass_prep_def(tbm, ibm, $3, $6,$8,$9));}

def p_camview_item_11(p):
    '''camview_item : PASS MERGE pass_samples opt_string READ string_list opt_function_list '''
    # { if (!have_p++)
    #                                 mi_api_function_delete(&camera->pass);
    #                           mi_api_output_type_identify(&tbm, &ibm, $4);
    #                           camera->pass = mi_api_function_append(camera->pass,
    #                                 mi_api_pass_merge_def(tbm, ibm, $3, $6,0,$7));}

def p_camview_item_12(p):
    '''camview_item : PASS MERGE pass_samples opt_string READ string_list WRITE T_STRING opt_function_list '''
    # { if (!have_p++)
    #                                 mi_api_function_delete(&camera->pass);
    #                           mi_api_output_type_identify(&tbm, &ibm, $4);
    #                           camera->pass = mi_api_function_append(camera->pass,
    #                                 mi_api_pass_merge_def(tbm,ibm, $3, $6,$8,$9));}

def p_camview_item_13(p):
    '''camview_item : PASS DELETE T_STRING '''
    # { if (!have_p++)
    #                                 mi_api_function_delete(&camera->pass);
    #                           camera->pass = mi_api_function_append(camera->pass,
    #                                 mi_api_pass_delete_def($3)); }

def p_camview_item_14(p):
    '''camview_item : PASS MASK boolean '''
    # { camera->pass_mask = $3; }

def p_camview_item_15(p):
    '''camview_item : VOLUME '''
    # { mi_api_function_delete(&camera->volume); }

def p_camview_item_16(p):
    '''camview_item : VOLUME _embed0_camview_item function_list '''
    # { camera->volume = mi_api_function_append(
    #                                                 camera->volume, $3); }

def p_camview_item_17(p):
    '''camview_item : ENVIRONMENT '''
    # { mi_api_function_delete(&camera->environment); }

def p_camview_item_18(p):
    '''camview_item : ENVIRONMENT _embed1_camview_item function_list '''
    # { camera->environment = mi_api_function_append(
    #                                                 camera->environment, $3); }

def p_camview_item_19(p):
    '''camview_item : LENS '''
    # { mi_api_function_delete(&camera->lens); }

def p_camview_item_20(p):
    '''camview_item : LENS _embed2_camview_item function_list '''
    # { camera->lens = mi_api_function_append(
    #                                                         camera->lens, $3); }

def p_camview_item_21(p):
    '''camview_item : FOCAL floating '''
    # { camera->focal = $2;
    #                           camera->orthographic = miFALSE; }

def p_camview_item_22(p):
    '''camview_item : FOCAL INFINITY '''
    # { camera->focal = 1;
    #                           camera->orthographic = miTRUE; }

def p_camview_item_23(p):
    '''camview_item : APERTURE floating '''
    # { camera->aperture = $2; }

def p_camview_item_24(p):
    '''camview_item : ASPECT floating '''
    # { camera->aspect = $2; }

def p_camview_item_25(p):
    '''camview_item : RESOLUTION T_INTEGER T_INTEGER '''
    # { camera->x_resolution = $2;
    #                           camera->y_resolution = $3; }

def p_camview_item_26(p):
    '''camview_item : OFFSET floating floating '''
    # { camera->x_offset = $2;
    #                           camera->y_offset = $3; }

def p_camview_item_27(p):
    '''camview_item : WINDOW T_INTEGER T_INTEGER T_INTEGER T_INTEGER '''
    # { camera->window.xl = $2;
    #                           camera->window.yl = $3;
    #                           camera->window.xh = $4;
    #                           camera->window.yh = $5; }

def p_camview_item_28(p):
    '''camview_item : CLIP floating floating '''
    # { camera->clip.min = $2;
    #                           camera->clip.max = $3; }

def p_camview_item_29(p):
    '''camview_item : DOF floating floating '''
    # { camera->focus  = $2;
    #                           camera->radius = $3; }


#======================================
# miFramebuffer : framebuffer
#======================================
#
#    framebuffer "name"
#        [ datatype "datatype" ]
#        [ filtering <bool> ]
#        [ filename "filename" ]
#        [ filetype "filetype" ]
#        [ compression "compression" ]
#        [ quality "quality" ]
#        [ colorprofile "color profile" ]
#        [ dod <bool> ]
#        [ dpi <int> ]
#        [ field "fieldname" ]
#        [ primary <bool> ]
#        [ user <bool> ]
#        [ useopacity <bool> ]

def p_camview_item_30(p):
    '''camview_item : FRAMEBUFFER T_STRING _embed3_camview_item buffer_list '''

def p_camview_item_31(p):
    '''camview_item : _embed4_camview_item data '''

def p__embed0_camview_item(p):
    '''_embed0_camview_item : '''
    # { if (!have_v++)
    #                                 mi_api_function_delete(&camera->volume); }

def p__embed1_camview_item(p):
    '''_embed1_camview_item : '''
    # { if (!have_e++)
    #                                 mi_api_function_delete(&camera->environment); }

def p__embed2_camview_item(p):
    '''_embed2_camview_item : '''
    # { if (!have_l++)
    #                                 mi_api_function_delete(&camera->lens); }

def p__embed3_camview_item(p):
    '''_embed3_camview_item : '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           if (ctx->buffer_name)
    #                               mi_api_release(ctx->buffer_name);
    #                           ctx->buffer_name = $2;
    #                         }

def p__embed4_camview_item(p):
    '''_embed4_camview_item : '''
    # { curr_datatag = &camera->userdata; }

def p_out_parms_1(p):
    '''out_parms : QUALITY T_INTEGER '''
    # { memset($$, 0, 8 * sizeof(float));
    #                           $$[0] = (float)$2; }

def p_out_parms_2(p):
    '''out_parms : EVEN '''
    # { memset($$, 0, 8 * sizeof(float));
    #                           $$[1] = 1.0; }

def p_out_parms_3(p):
    '''out_parms : ODD '''
    # { memset($$, 0, 8 * sizeof(float));
    #                           $$[1] = 2.0; }

def p_out_parms_4(p):
    '''out_parms : DOD '''
    # { memset($$, 0, 8 * sizeof(float));
    #                           $$[4] = 1.0; }

def p_out_parms_5(p):
    '''out_parms : DPI floating '''
    # { memset($$, 0, 8 * sizeof(float));
    #                           $$[6] = $2; }

def p_out_parms_6(p):
    '''out_parms : COMPRESS T_STRING '''
    # { memset($$, 0, 8 * sizeof(float));
    #                           if (!strcmp($2, "none"))
    #                                 $$[0] = 1.0;
    #                           else if (!strcmp($2, "piz"))
    #                                 $$[0] = 2.0;
    #                           else if (!strcmp($2, "zip"))
    #                                 $$[0] = 3.0;
    #                           else if (!strcmp($2, "rle"))
    #                                 $$[0] = 4.0;
    #                           else if (!strcmp($2, "pxr24"))
    #                                 $$[0] = 5.0;
    #                           else {
    #                                 mi_api_error("%s is not a valid compression "
    #                                              "type, using rle compression", $2);
    #                                 $$[0] = 4.0;
    #                           }
    #                         }

def p_frame_number_1(p):
    '''frame_number : FRAME T_INTEGER '''
    # { camera->frame       = $2;
    #                           camera->frame_time  = 0;
    #                           camera->frame_field = 0; }

def p_frame_number_2(p):
    '''frame_number : FRAME T_INTEGER floating '''
    # { camera->frame       = $2;
    #                           camera->frame_time  = $3;
    #                           camera->frame_field = 0; }

def p_colorspace_set_1(p):
    '''colorspace_set :  '''
    # { $$ = 0; }

def p_colorspace_set_2(p):
    '''colorspace_set : COLORPROFILE symbol '''
    # { $$ = $2; }

def p_pass_samples_1(p):
    '''pass_samples :  '''
    # { $$ = ~0; }

def p_pass_samples_2(p):
    '''pass_samples : SAMPLES T_INTEGER '''
    # { $$ = $2; }

def p_string_list_1(p):
    '''string_list : _embed0_string_list '[' strings ']' '''

def p__embed0_string_list(p):
    '''_embed0_string_list : '''
    # { $$ = stringlist
    #                              = mi_api_dlist_create(miDLIST_POINTER); }

def p_strings_1(p):
    '''strings : T_STRING '''
    # { mi_api_dlist_add(stringlist, $1); }

def p_strings_2(p):
    '''strings : strings ',' T_STRING '''
    # { mi_api_dlist_add(stringlist, $3); }

def p_buffer_list_1(p):
    '''buffer_list :  '''

def p_buffer_list_2(p):
    '''buffer_list : buffer_list buffer_item '''

def p_buffer_item_1(p):
    '''buffer_item : DATATYPE T_STRING '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "datatype", $2);
    #                           mi_api_release($2);
    #                         }

def p_buffer_item_2(p):
    '''buffer_item : FILENAME T_STRING '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "filename", $2);
    #                           mi_api_release($2);
    #                         }

def p_buffer_item_3(p):
    '''buffer_item : FILETYPE T_STRING '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "filetype", $2);
    #                           mi_api_release($2);
    #                         }

def p_buffer_item_4(p):
    '''buffer_item : FILTERING boolean '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "filtering", $2 == miTRUE);
    #                         }

def p_buffer_item_5(p):
    '''buffer_item : COLORPROFILE T_STRING '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "colorprofile", $2);
    #                           mi_api_release($2);
    #                         }

def p_buffer_item_6(p):
    '''buffer_item : COMPRESSION T_STRING '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "compression", $2);
    #                           mi_api_release($2);
    #                         }

def p_buffer_item_7(p):
    '''buffer_item : FIELD T_STRING '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "field", $2);
    #                           mi_api_release($2);
    #                         }

def p_buffer_item_8(p):
    '''buffer_item : QUALITY T_INTEGER '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "quality", (int)$2);
    #                         }

def p_buffer_item_9(p):
    '''buffer_item : DOD boolean '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "dod", $2 == miTRUE);
    #                         }

def p_buffer_item_10(p):
    '''buffer_item : DPI T_INTEGER '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "dpi", $2);
    #                         }

def p_buffer_item_11(p):
    '''buffer_item : PRIMARY boolean '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "primary", $2 == miTRUE);
    #                         }

def p_buffer_item_12(p):
    '''buffer_item : USEOPACITY boolean '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "useopacity", $2 == miTRUE);
    #                         }

def p_buffer_item_13(p):
    '''buffer_item : USEPRIMARY boolean '''
    # {
    #                           Edit_fb fb(camera->buffertag);
    #                           fb->set(ctx->buffer_name, "useprimary", $2 == miTRUE);
    #                         }


#======================================
# miInstance : instance
#======================================
#
#    instance "name" "element" | geometry function
#        [ hide on|off ]
#        [ visible on|off ]
#        [ shadow on|off ]
#        [ shadow mode ]
#        [ shadowmap on|off ]
#        [ trace on|off ]
#        [ reflection mode ]
#        [ refraction mode ]
#        [ transparency mode ]
#        [ caustic on|off ]
#        [ caustic [mode] ]
#        [ globillum on|off ]
#        [ globillum [mode] ]
#        [ finalgather [mode] ]
#        [ transform [matrix]]
#        [ motion transform [matrix]]
#        [ face [front|back|both]]
#        [ motion off ]
#        [ override ]
#        [ material "material_name" ]
#        [ material [ "material_name" [, "material_name" ...]] ]
#        [ light ["exclusive"] [ ["light_name" [, "light_name" ...]]] ]
#        [ light shadow ["exclusive"] [ ["light_name" [, "light_name" ...]]] ]
#        [ approximate [approximation [, approximation ...]] ]
#        [ shading samples samplesscalar ]
#        [ tag labelint ]
#        [ data ["data_name"] ]
#        [ ( parameters ) ]
#    end instance  


def p_instance_1(p):
    '''instance : INSTANCE symbol _embed0_instance inst_item inst_func inst_flags inst_params _embed1_instance END INSTANCE '''
    type = p[1]
    symbol = p[2]
    item = p[4]
    func = p[5]
    flags = p[6]
    parms = p[7]
    text = '' # not dealing with creating a text repr for now
    if debug: print "INSTANCE", symbol, item, func, flags, parms
    #p[0] = p.lexer.curr_inst
    p[0] = NamedEntity( type, text, symbol if symbol else func, data=item, attrs=flags)

def p__embed0_instance(p):
    '''_embed0_instance : '''
    # { curr_inst = mi_api_instance_begin($2);
    #                           if (!curr_inst) {
    #                                   memset(&dummy_inst, 0, sizeof(dummy_inst));
    #                                   curr_inst = &dummy_inst;
    #                           }
    #                           override = miFALSE; }
    #print "EMBED INST", p[-1]
    #p.lexer.curr_inst = Instance(p[-1])
    
def p__embed1_instance(p):
    '''_embed1_instance : '''
    # { mi_api_instance_end($4, $5, $7); }
    #print "_embed1_instance",  p[-4], p[-3], p[-2], p[-1]
    #p.lexer.curr_inst.item = p[-4]
    #p.lexer.curr_inst.func = p[-3]
    #p.lexer.curr_inst.params = p[-1]

def p_inst_item_1(p):
    '''inst_item :  '''
    # { $$ = 0; }

def p_inst_item_2(p):
    '''inst_item : symbol '''
    # { $$ = $1; }
    p[0] = p[1]
    
def p_inst_func_1(p):
    '''inst_func :  '''
    # { $$ = miNULLTAG; }
    
def p_inst_func_2(p):
    '''inst_func : GEOMETRY function_list '''
    # { $$ = $2; }
    p[0] = p[2]

def p_inst_flags_1(p):
    '''inst_flags :  '''
    p[0] = []

def p_inst_flags_2(p):
    '''inst_flags : inst_flag inst_flags '''
    if p[2] is not None:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_inst_flag_1(p):
    '''inst_flag : VISIBLE boolean '''
    # { curr_inst->visible    = $2 ? 2 : 1; }
    
    #p.lexer.curr_inst.visible = p[2]
    #p[0] = ( p[1], p[2] )


def p_inst_flag_2(p):
    '''inst_flag : SHADOW boolean '''
    # { curr_inst->shadow     = $2 ? 0x03 : 0x06; }
    
    #p.lexer.curr_inst.shadow = p[2]
    #p[0] = ( p[1], p[2] )


def p_inst_flag_3(p):
    '''inst_flag : SHADOW T_INTEGER '''
    # { curr_inst->shadow     = ($2 & 0x0f); }
    
    #p[0] = ( p[1], p[2] )


def p_inst_flag_4(p):
    '''inst_flag : SHADOWMAP boolean '''
    # { curr_inst->shadowmap  = $2 ? 2 : 1; }
    
    #p[0] = ( p[1], p[2] )


def p_inst_flag_5(p):
    '''inst_flag : TRACE boolean '''
    # { curr_inst->reflection =
    #                           curr_inst->refraction = $2 ? 0x03 : 0x0c;
    #                           curr_inst->finalgather= $2 ? 0x23 : 0x10; }
    p[0] = ( p[1], p[2] )


def p_inst_flag_6(p):
    '''inst_flag : REFLECTION T_INTEGER '''
    # { curr_inst->reflection = ($2 & 0x0f); }
    p[0] = ( p[1], p[2] )

  
def p_inst_flag_7(p):
    '''inst_flag : REFRACTION T_INTEGER '''
    # { curr_inst->refraction = ($2 & 0x0f); }
    p[0] = ( p[1], p[2] )


def p_inst_flag_8(p):
    '''inst_flag : TRANSPARENCY T_INTEGER '''
    # { curr_inst->transparency = ($2 & 0x0f); }
    p[0] = ( p[1], p[2] )


def p_inst_flag_9(p):
    '''inst_flag : FACE FRONT '''
    # { curr_inst->face       = 'f'; }
    p[0] = ( p[1], p[2] )


def p_inst_flag_10(p):
    '''inst_flag : FACE BACK '''
    # { curr_inst->face       = 'b'; }
    p[0] = ( p[1], p[2] )


def p_inst_flag_11(p):
    '''inst_flag : FACE BOTH '''
    # { curr_inst->face       = 'a'; }
    p[0] = ( p[1], p[2] )


def p_inst_flag_12(p):
    '''inst_flag : SELECT boolean '''
    # { curr_inst->select     = $2 ? 2 : 1; }
    p[0] = ( p[1], p[2] )


def p_inst_flag_13(p):
    '''inst_flag : CAUSTIC '''
    # { curr_inst->caustic   &= 0x30;
    #                           curr_inst->caustic   |= 0x03; }
    p[0] = ( p[1], None )


def p_inst_flag_14(p):
    '''inst_flag : CAUSTIC boolean '''
    # { curr_inst->caustic   &= 0x0f;
    #                           curr_inst->caustic   |= $2 ? 0x20 : 0x10; }
    p[0] = ( p[1], p[2] )


def p_inst_flag_15(p):
    '''inst_flag : CAUSTIC T_INTEGER '''
    # { curr_inst->caustic   &= 0x30;
    #                           curr_inst->caustic   |= ($2 & 0x0f); }
    p[0] = ( p[1], p[2] )


def p_inst_flag_16(p):
    '''inst_flag : GLOBILLUM '''
    # { curr_inst->globillum &= 0x30;
    #                           curr_inst->globillum |= 0x03; }


def p_inst_flag_17(p):
    '''inst_flag : GLOBILLUM boolean '''
    # { curr_inst->globillum &= 0x0f;
    #                           curr_inst->globillum |= $2 ? 0x20 : 0x10; }


def p_inst_flag_18(p):
    '''inst_flag : GLOBILLUM T_INTEGER '''
    # { curr_inst->globillum &= 0x30;
    #                           curr_inst->globillum |= ($2 & 0x0f); }


def p_inst_flag_19(p):
    '''inst_flag : FINALGATHER '''
    # { curr_inst->finalgather &= 0x30;
    #                           curr_inst->finalgather |= 0x03; }


def p_inst_flag_20(p):
    '''inst_flag : FINALGATHER boolean '''
    # { curr_inst->finalgather &= 0x0f;
    #                           curr_inst->finalgather |= $2 ? 0x20 : 0x10; }


def p_inst_flag_21(p):
    '''inst_flag : FINALGATHER T_INTEGER '''
    # { curr_inst->finalgather &= 0x30;
    #                           curr_inst->finalgather |= ($2 & 0x0f); }


def p_inst_flag_22(p):
    '''inst_flag : SHADING SAMPLES floating '''
    # { curr_inst->shading_samples = $3; }


def p_inst_flag_23(p):
    '''inst_flag : HARDWARE '''
    # { curr_inst->hardware   = 2; }


def p_inst_flag_24(p):
    '''inst_flag : HARDWARE boolean '''
    # { curr_inst->hardware   = $2 ? 2 : 1; }


def p_inst_flag_25(p):
    '''inst_flag : HIDE boolean '''
    # { curr_inst->off = $2; }


def p_inst_flag_26(p):
    '''inst_flag : TRANSFORM '''
    # { curr_inst->tf.function = miNULLTAG;
    #                           mi_matrix_ident(curr_inst->tf.global_to_local); }
    p[0] = ( p[1], p[2] )


def p_inst_flag_27(p):
    '''inst_flag : TRANSFORM function '''
    # { curr_inst->tf.function = $2;
    #                           mi_matrix_ident(curr_inst->tf.global_to_local); }
    p[0] = ( p[1], p[2] )

def p_inst_flag_28(p):
    '''inst_flag : transform '''
    # { curr_inst->tf.function = miNULLTAG;
    #                           mi_matrix_copy(
    #                                 curr_inst->tf.global_to_local, $1);
    #                           if (!mi_matrix_invert(curr_inst->tf.local_to_global,
    #                                                curr_inst->tf.global_to_local)){
    #                                 mi_api_warning("singular matrix, using "
    #                                                                 "identity");
    #                                 mi_matrix_ident(curr_inst->tf.global_to_local);
    #                                 mi_matrix_ident(curr_inst->tf.local_to_global);
    #                         }}
    p[0] = p[1]


def p_inst_flag_29(p):
    '''inst_flag : MOTION OFF '''
    # { mi_matrix_null(curr_inst->motion_transform);
    #                           curr_inst->gen_motion = miGM_OFF; }


def p_inst_flag_30(p):
    '''inst_flag : MOTION TRANSFORM '''
    # { mi_matrix_null(curr_inst->motion_transform);
    #                           curr_inst->gen_motion = miGM_INHERIT; }


def p_inst_flag_31(p):
    '''inst_flag : MOTION transform '''
    # { mi_matrix_copy(curr_inst->motion_transform, $2);
    #                           curr_inst->gen_motion = miGM_TRANSFORM; }

def p_inst_flag_32(p):
    '''inst_flag : LIGHT incl_excl light_list '''
    # { curr_inst->exclusive   = $2;   
    #                           curr_inst->light_list = $3; }
    p[0] = ( p[1], (p[2], p[3]) )

def p_inst_flag_33(p):
    '''inst_flag : LIGHT SHADOW incl_excl light_list '''
    # { curr_inst->shadow_excl = $3;
    #                           curr_inst->shadow_list = $4; }

def p_inst_flag_34(p):
    '''inst_flag : MATERIAL _embed0_inst_flag inst_mtl '''
    p[0] = (p[1], p[3])
    
def p_inst_flag_35(p):
    '''inst_flag : TAG T_INTEGER '''
    # { curr_inst->label = $2; }

def p_inst_flag_36(p):
    '''inst_flag : _embed1_inst_flag data '''

def p_inst_flag_37(p):
    '''inst_flag : OVERRIDE '''
    # { override = miTRUE; }

def p_inst_flag_38(p):
    '''inst_flag : APPROXIMATE '''
    # { mi_api_instance_approx(0, miFALSE); }

def p_inst_flag_39(p):
    '''inst_flag : APPROXIMATE _embed2_inst_flag '[' inst_approx_arr ']' '''

def p_inst_flag_40(p):
    '''inst_flag : dummy_attribute '''

def p__embed0_inst_flag(p):
    '''_embed0_inst_flag : '''
    # { curr_inst->material       = miNULLTAG;
    #                           curr_inst->mtl_array_size = 0;
    #                           curr_inst->mtl_override   = miFALSE; }

def p__embed1_inst_flag(p):
    '''_embed1_inst_flag : '''
    # { curr_datatag = &curr_inst->userdata; }

def p__embed2_inst_flag(p):
    '''_embed2_inst_flag : '''
    # { miAPPROX_DEFAULT(approx);
    #                           curr_inst->approx_override = override;
    #                           override = miFALSE; }

def p_inst_params_1(p):
    '''inst_params :  '''
    # { $$ = (miTag)-1; }

def p_inst_params_2(p):
    '''inst_params : '(' ')' '''
    # { $$ = miNULLTAG; }

def p_inst_params_3(p):
    '''inst_params : '(' _embed0_inst_params parameter_seq comma_rparen '''
    # { $$ = mi_api_function_call_end(0); }

def p__embed0_inst_params(p):
    '''_embed0_inst_params : '''
    # { if (!ctx->inheritance_func)
    #                             mi_api_error("no inheritance function in options");
    #                           else
    #                             mi_api_function_call(mi_api_strdup(
    #                                                  ctx->inheritance_func)); }

def p_comma_rparen_1(p):
    '''comma_rparen : ')' '''

def p_comma_rparen_2(p):
    '''comma_rparen : ',' ')' '''

def p_inst_mtl_1(p):
    '''inst_mtl :  '''

def p_inst_mtl_2(p):
    '''inst_mtl : symbol '''
    # { curr_inst->material     = mi_api_material_lookup($1);
    #                           curr_inst->mtl_override = override;
    #                           override = miFALSE; }
    p[0] = p[1]

def p_inst_mtl_3(p):
    '''inst_mtl : '[' _embed0_inst_mtl inst_mtl_array ']' '''
    # { curr_inst->mtl_array_size = taglist->nb;
    #                           curr_inst->material       = mi_api_taglist(taglist);
    #                           curr_inst->mtl_override   = override; }
    p[0] = p[3]

def p__embed0_inst_mtl(p):
    '''_embed0_inst_mtl : '''
    # { taglist = mi_api_dlist_create(miDLIST_TAG); }

def p_inst_mtl_array_1(p):
    '''inst_mtl_array : symbol _embed0_inst_mtl_array inst_mtl_next '''
    if p[3]:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]
    
def p__embed0_inst_mtl_array(p):
    '''_embed0_inst_mtl_array : '''
    # { mi_api_dlist_add(taglist,
    #                                 (void *)(miIntptr)mi_api_material_lookup($1));}

def p_inst_mtl_next_1(p):
    '''inst_mtl_next :  '''

def p_inst_mtl_next_2(p):
    '''inst_mtl_next : ',' '''

def p_inst_mtl_next_3(p):
    '''inst_mtl_next : ',' inst_mtl_array '''
    p[0] = p[2]

def p_inst_approx_arr_1(p):
    '''inst_approx_arr : approx_flags APPROXIMATE s_approx_tech ALL _embed0_inst_approx_arr inst_approx_nxt '''

def p_inst_approx_arr_2(p):
    '''inst_approx_arr : approx_flags APPROXIMATE DISPLACE s_approx_tech ALL _embed1_inst_approx_arr inst_approx_nxt '''

def p__embed0_inst_approx_arr(p):
    '''_embed0_inst_approx_arr : '''
    # { mi_api_instance_approx(&approx, miFALSE);
    #                           miAPPROX_DEFAULT(approx); }

def p__embed1_inst_approx_arr(p):
    '''_embed1_inst_approx_arr : '''
    # { mi_api_instance_approx(&approx, miTRUE);
    #                           miAPPROX_DEFAULT(approx); }

def p_inst_approx_nxt_1(p):
    '''inst_approx_nxt :  '''

def p_inst_approx_nxt_2(p):
    '''inst_approx_nxt : ',' '''

def p_inst_approx_nxt_3(p):
    '''inst_approx_nxt : ',' inst_approx_arr '''

def p_incl_excl_1(p):
    '''incl_excl :  '''
    # { $$ = 0 ; /* not exclusive */ }
    
def p_incl_excl_2(p):
    '''incl_excl : T_STRING '''
    # { if(!strcmp($1, "exclusive")) {
    #                            $$ = 1;
    #                       } else {
    #                            $$ = 0;
    #                            mi_api_nwarning(127,"instance light list modifier \"%s\"" 
    #                             " is not \"exclusive\" -- using non-exclusive light list!", $1);
    #                       }
    #                       mi_mem_release($1);
    #                     }
    p[0] = p[1]
    
def p_light_list_1(p):
    '''light_list : '[' _embed0_light_list light_list_element ']' '''
    # { $$ = mi_api_light_list_end(); }

def p_light_list_2(p):
    '''light_list : '[' ']' '''
    # { mi_api_light_list_begin();
    #                       $$ = mi_api_light_list_end(); }
    p[0] = []
    
def p__embed0_light_list(p):
    '''_embed0_light_list : '''
    # { mi_api_light_list_begin(); }

def p_light_list_element_1(p):
    '''light_list_element : symbol '''
    # { mi_api_light_list_add($1); }
    p[0] = [p[1]]

def p_light_list_element_2(p):
    '''light_list_element : light_list_element light_list_next symbol '''
    # { mi_api_light_list_add($3); }
    p[0] = p[1] + [p[2]]
    
def p_light_list_next_1(p):
    '''light_list_next :  '''

def p_light_list_next_2(p):
    '''light_list_next : ',' '''

#======================================
# miGroup : instgroup
#======================================
#
#    instgroup "name "
#        "name"
#        [ tag labelint ]
#        [ data [ "data_name" ]]
#        ...
#    end instgroup

def p_instgroup_1(p):
    '''instgroup : INSTGROUP symbol _embed0_instgroup group_flags group_kids END INSTGROUP '''
    # { mi_api_instgroup_end(); }

def p__embed0_instgroup(p):
    '''_embed0_instgroup : '''
    # { curr_group = mi_api_instgroup_begin($2);
    #                           mi_api_instgroup_clear(); }

def p_group_flags_1(p):
    '''group_flags :  '''

def p_group_flags_2(p):
    '''group_flags : group_flag group_flags '''

def p_group_flag_1(p):
    '''group_flag : MERGE floating '''
    # { curr_group->merge = $2;
    #                           curr_group->merge_group = $2 >= miMERGE_MIN; }

def p_group_flag_2(p):
    '''group_flag : TAG T_INTEGER '''
    # { curr_group->label = $2; }

def p_group_flag_3(p):
    '''group_flag : _embed0_group_flag data '''

def p_group_flag_4(p):
    '''group_flag : dummy_attribute '''

def p__embed0_group_flag(p):
    '''_embed0_group_flag : '''
    # { curr_datatag = &curr_group->userdata; }

def p_group_kids_1(p):
    '''group_kids :  '''

def p_group_kids_2(p):
    '''group_kids : group_kids symbol '''
    # { mi_api_instgroup_additem($2); }

#======================================
# miAssembly : assembly
#======================================
#
#    assembly "assembly_name"
#        box [xmin ymin zmin xmax ymax zmax]
#        [ motion box [xmin ymin zmin xmax ymax zmax] ]
#        file "file_name"
#    end assembly

def p_assembly_1(p):
    '''assembly : ASSEMBLY symbol '''
    # { curr_assembly = mi_api_assembly_begin($2); }

def p_assembly_2(p):
    '''assembly : assembly_flags END ASSEMBLY '''
    # { mi_api_assembly_end(); }

def p_assembly_flags_1(p):
    '''assembly_flags : assembly_flag assembly_flags '''

def p_assembly_flags_2(p):
    '''assembly_flags : assembly_flag '''

def p_assembly_flag_1(p):
    '''assembly_flag : BOX vector vector '''
    # { curr_assembly->bbox_min = $2;
    #                           curr_assembly->bbox_max = $3; }

def p_assembly_flag_2(p):
    '''assembly_flag : BOX '''
    # { curr_assembly->bbox_min = nullvec;
    #                           curr_assembly->bbox_max = nullvec; }

def p_assembly_flag_3(p):
    '''assembly_flag : MOTION BOX vector vector '''
    # { curr_assembly->bbox_min_m = $3;
    #                           curr_assembly->bbox_max_m = $4; }

def p_assembly_flag_4(p):
    '''assembly_flag : MOTION BOX '''
    # { curr_assembly->bbox_min_m = nullvec;
    #                           curr_assembly->bbox_max_m = nullvec; }

def p_assembly_flag_5(p):
    '''assembly_flag : FILE T_STRING '''
    # { mi_api_assembly_filename($2); }






def p_function_decl_1(p):
    '''function_decl : shret_type_nosh T_STRING parm_decl_list '''
    # { mi_api_funcdecl_begin($1, $2, $3);
    #                           mi_api_funcdecl_end(); }

def p_function_decl_2(p):
    '''function_decl : SHADER shret_type T_STRING parm_decl_list _embed0_function_decl declare_req_seq END DECLARE '''
    # { mi_api_funcdecl_end(); }

def p__embed0_function_decl(p):
    '''_embed0_function_decl : '''
    # { if (!(curr_decl = mi_api_funcdecl_begin($2,$3,$4))){
    #                                 memset(&dummy_decl, 0, sizeof(dummy_decl));
    #                                 curr_decl = &dummy_decl;
    #                           } }

def p_shret_type_1(p):
    '''shret_type : shret_type_nosh '''
    # { $$ = $1; }

def p_shret_type_2(p):
    '''shret_type : SHADER '''
    # { $$ = mi_api_parameter_decl(miTYPE_SHADER, 0, 0); }

def p_shret_type_nosh_1(p):
    '''shret_type_nosh :  '''
    # { $$ = mi_api_parameter_decl(miTYPE_COLOR, 0, 0); }

def p_shret_type_nosh_2(p):
    '''shret_type_nosh : simple_type '''
    # { $$ = mi_api_parameter_decl((miParam_type)$1, 0, 0); }

def p_shret_type_nosh_3(p):
    '''shret_type_nosh : STRUCT '{' shret_decl_seq '}' '''
    # { miParameter *parm =
    #                                 mi_api_parameter_decl(miTYPE_STRUCT, 0, 0);
    #                           mi_api_parameter_child(parm, $3);
    #                           $$ = parm; }

def p_shret_decl_seq_1(p):
    '''shret_decl_seq : shret_decl_seq ',' shret_decl '''
    # { $$ = mi_api_parameter_append($1, $3); }

def p_shret_decl_seq_2(p):
    '''shret_decl_seq : shret_decl '''
    # { $$ = $1; }

def p_shret_decl_1(p):
    '''shret_decl : simple_type symbol '''
    # { $$ = mi_api_parameter_decl((miParam_type)$1, $2, 0); }

def p_shret_decl_2(p):
    '''shret_decl : SHADER symbol '''
    # { $$ = mi_api_parameter_decl(miTYPE_SHADER, $2, 0); }

def p_shret_decl_3(p):
    '''shret_decl : DATA symbol '''
    # { $$ = mi_api_parameter_decl(miTYPE_DATA,   $2, 0); }

def p_parm_decl_list_1(p):
    '''parm_decl_list : '(' parm_decl_seq ')' '''
    # { $$ = $2; }

def p_parm_decl_list_2(p):
    '''parm_decl_list : '(' parm_decl_seq ',' ')' '''
    # { $$ = $2; }

def p_parm_decl_list_3(p):
    '''parm_decl_list : '(' ')' '''
    # { $$ = 0; }

def p_parm_decl_seq_1(p):
    '''parm_decl_seq : parm_decl_seq ',' parm_decl '''
    # { $$ = mi_api_parameter_append($1, $3); }

def p_parm_decl_seq_2(p):
    '''parm_decl_seq : parm_decl '''
    # { $$ = $1; }

def p_parm_decl_1(p):
    '''parm_decl : decl_simple decl_default '''
    # { $$ = $1; }

def p_parm_decl_2(p):
    '''parm_decl : SHADER symbol '''
    # { $$ = mi_api_parameter_decl(miTYPE_SHADER, $2, 0); }

def p_parm_decl_3(p):
    '''parm_decl : DATA symbol '''
    # { $$ = mi_api_parameter_decl(miTYPE_DATA,   $2, 0); }

def p_parm_decl_4(p):
    '''parm_decl : STRUCT symbol '{' parm_decl_seq '}' '''
    # { miParameter *parm =
    #                                 mi_api_parameter_decl(miTYPE_STRUCT, $2, 0);
    #                           mi_api_parameter_child(parm, $4);
    #                           $$ = parm; }

def p_parm_decl_5(p):
    '''parm_decl : ARRAY parm_decl '''
    # { miParameter *parm =
    #                                 mi_api_parameter_decl(miTYPE_ARRAY, 0, 0);
    #                           mi_api_parameter_child(parm, $2);
    #                           $$ = parm; }

def p_decl_simple_1(p):
    '''decl_simple : simple_type symbol '''
    # { $$ = mi_api_parameter_decl((miParam_type) $1, $2, 0); }

def p_simple_type_1(p):
    '''simple_type : BOOLEAN '''
    # { $$ = miTYPE_BOOLEAN; }

def p_simple_type_2(p):
    '''simple_type : INTEGER '''
    # { $$ = miTYPE_INTEGER; }

def p_simple_type_3(p):
    '''simple_type : SCALAR '''
    # { $$ = miTYPE_SCALAR; }

def p_simple_type_4(p):
    '''simple_type : STRING '''
    # { $$ = miTYPE_STRING; }

def p_simple_type_5(p):
    '''simple_type : COLOR '''
    # { $$ = miTYPE_COLOR; }

def p_simple_type_6(p):
    '''simple_type : VECTOR '''
    # { $$ = miTYPE_VECTOR; }

def p_simple_type_7(p):
    '''simple_type : TRANSFORM '''
    # { $$ = miTYPE_TRANSFORM; }

def p_simple_type_8(p):
    '''simple_type : SCALAR TEXTURE '''
    # { $$ = miTYPE_SCALAR_TEX; }

def p_simple_type_9(p):
    '''simple_type : VECTOR TEXTURE '''
    # { $$ = miTYPE_VECTOR_TEX; }

def p_simple_type_10(p):
    '''simple_type : COLOR TEXTURE '''
    # { $$ = miTYPE_COLOR_TEX; }

def p_simple_type_11(p):
    '''simple_type : LIGHTPROFILE '''
    # { $$ = miTYPE_LIGHTPROFILE; }

def p_simple_type_12(p):
    '''simple_type : SPECTRUM '''
    # { $$ = miTYPE_SPECTRUM; }

def p_simple_type_13(p):
    '''simple_type : LIGHT '''
    # { $$ = miTYPE_LIGHT; }

def p_simple_type_14(p):
    '''simple_type : MATERIAL '''
    # { $$ = miTYPE_MATERIAL; }

def p_simple_type_15(p):
    '''simple_type : GEOMETRY '''
    # { $$ = miTYPE_GEOMETRY; }

def p_decl_default_1(p):
    '''decl_default :  '''

def p_decl_default_2(p):
    '''decl_default : DEFAULT decl_def_values '''

def p_decl_def_values_1(p):
    '''decl_def_values :  '''

def p_decl_def_values_2(p):
    '''decl_def_values : decl_def_value decl_def_values '''

def p_decl_def_value_1(p):
    '''decl_def_value : boolean '''
    # { int value = $1;
    #                           mi_api_parameter_default(miTYPE_BOOLEAN, &value); }

def p_decl_def_value_2(p):
    '''decl_def_value : T_INTEGER '''
    # { int value = $1;
    #                           mi_api_parameter_default(miTYPE_INTEGER, &value); }

def p_decl_def_value_3(p):
    '''decl_def_value : T_FLOAT '''
    # { float value = $1;
    #                           mi_api_parameter_default(miTYPE_SCALAR,  &value); }

def p_declare_req_seq_1(p):
    '''declare_req_seq :  '''

def p_declare_req_seq_2(p):
    '''declare_req_seq : declare_req declare_req_seq '''

def p_declare_req_1(p):
    '''declare_req : gui '''

def p_declare_req_2(p):
    '''declare_req : SCANLINE OFF '''
    # { curr_decl->phen.scanline = 1; }

def p_declare_req_3(p):
    '''declare_req : SCANLINE ON '''
    # { curr_decl->phen.scanline = 2; }

def p_declare_req_4(p):
    '''declare_req : TRACE OFF '''
    # { curr_decl->phen.trace = 1; }

def p_declare_req_5(p):
    '''declare_req : TRACE ON '''
    # { curr_decl->phen.trace = 2; }

def p_declare_req_6(p):
    '''declare_req : SHADOW OFF '''
    # { curr_decl->phen.shadow = 1; }

def p_declare_req_7(p):
    '''declare_req : SHADOW ON '''
    # { curr_decl->phen.shadow = 2; }

def p_declare_req_8(p):
    '''declare_req : SHADOW SORT '''
    # { curr_decl->phen.shadow = 'l'; }

def p_declare_req_9(p):
    '''declare_req : SHADOW SEGMENTS '''
    # { curr_decl->phen.shadow = 's'; }

def p_declare_req_10(p):
    '''declare_req : FACE FRONT '''
    # { curr_decl->phen.face = 'f'; }

def p_declare_req_11(p):
    '''declare_req : FACE BACK '''
    # { curr_decl->phen.face = 'b'; }

def p_declare_req_12(p):
    '''declare_req : FACE BOTH '''
    # { curr_decl->phen.face = 'a'; }

def p_declare_req_13(p):
    '''declare_req : TEXTURE T_INTEGER '''
    # { curr_decl->phen.mintextures = $2; }

def p_declare_req_14(p):
    '''declare_req : BUMP T_INTEGER '''
    # { curr_decl->phen.minbumps = $2; }

def p_declare_req_15(p):
    '''declare_req : DERIVATIVE '''
    # { curr_decl->phen.deriv1 =
    #                           curr_decl->phen.deriv2 = 0; }

def p_declare_req_16(p):
    '''declare_req : DERIVATIVE T_INTEGER '''
    # { if ($2 == 1)
    #                                 curr_decl->phen.deriv1 = miTRUE;
    #                           else if ($2 == 2)
    #                                 curr_decl->phen.deriv2 = miTRUE;
    #                           else
    #                                 mi_api_error("derivative not 1 or 2"); }

def p_declare_req_17(p):
    '''declare_req : DERIVATIVE T_INTEGER T_INTEGER '''
    # { if ($2 == 1 || $3 == 1)
    #                                 curr_decl->phen.deriv1 = miTRUE;
    #                           else if ($2 == 2 || $3 == 2)
    #                                 curr_decl->phen.deriv2 = miTRUE;
    #                           if ($2 != 1 && $2 != 2 || $3 != 1 && $3 != 2)
    #                                 mi_api_error("derivative not 1 or 2"); }

def p_declare_req_18(p):
    '''declare_req : OBJECT SPACE '''
    # { curr_decl->phen.render_space = 'o'; }

def p_declare_req_19(p):
    '''declare_req : CAMERA SPACE '''
    # { curr_decl->phen.render_space = 'c'; }

def p_declare_req_20(p):
    '''declare_req : MIXED SPACE '''
    # { curr_decl->phen.render_space = 'm'; }

def p_declare_req_21(p):
    '''declare_req : WORLD SPACE '''
    # { mi_api_warning("world space statement ignored"); }

def p_declare_req_22(p):
    '''declare_req : PARALLEL '''
    # { curr_decl->phen.parallel = miTRUE; }

def p_declare_req_23(p):
    '''declare_req : VOLUME LEVEL T_INTEGER '''
    # { curr_decl->phen.volume_level = $3; }

def p_declare_req_24(p):
    '''declare_req : VERSION T_INTEGER '''
    # { curr_decl->version = $2; }

def p_declare_req_25(p):
    '''declare_req : APPLY apply_list '''
    # { curr_decl->apply = $2; }

def p_declare_req_26(p):
    '''declare_req : HARDWARE _embed0_declare_req hardware_list '''
    # { curr_decl->hardware = mi_api_hardware_end(curr_hw); }

def p__embed0_declare_req(p):
    '''_embed0_declare_req : '''
    # { curr_hw = mi_api_hardware_begin(); }

def p_hardware_list_1(p):
    '''hardware_list :  '''

def p_hardware_list_2(p):
    '''hardware_list : '(' hardware_seq ')' '''

def p_hardware_list_3(p):
    '''hardware_list : '(' hardware_seq ',' ')' '''

def p_hardware_seq_1(p):
    '''hardware_seq :  '''

def p_hardware_seq_2(p):
    '''hardware_seq : hardware_seq ',' hardware_attr '''

def p_hardware_seq_3(p):
    '''hardware_seq : hardware_attr '''

def p_hardware_attr_1(p):
    '''hardware_attr : UNIFORM T_STRING '''
    # { mi_api_hardware_attr(curr_hw, 'u', $2); }

def p_hardware_attr_2(p):
    '''hardware_attr : VERTEX T_STRING '''
    # { mi_api_hardware_attr(curr_hw, 'v', $2); }

def p_hardware_attr_3(p):
    '''hardware_attr : FRAGMENT T_STRING '''
    # { mi_api_hardware_attr(curr_hw, 'f', $2); }

def p_apply_list_1(p):
    '''apply_list : apply '''
    # { $$ = $1; }

def p_apply_list_2(p):
    '''apply_list : apply_list ',' apply '''
    # { $$ = $1 | $3; }

def p_apply_1(p):
    '''apply : LENS '''
    # { $$ = miAPPLY_LENS;            }

def p_apply_2(p):
    '''apply : MATERIAL '''
    # { $$ = miAPPLY_MATERIAL;        }

def p_apply_3(p):
    '''apply : LIGHT '''
    # { $$ = miAPPLY_LIGHT;           }

def p_apply_4(p):
    '''apply : SHADOW '''
    # { $$ = miAPPLY_SHADOW;          }

def p_apply_5(p):
    '''apply : ENVIRONMENT '''
    # { $$ = miAPPLY_ENVIRONMENT;     }

def p_apply_6(p):
    '''apply : VOLUME '''
    # { $$ = miAPPLY_VOLUME;          }

def p_apply_7(p):
    '''apply : TEXTURE '''
    # { $$ = miAPPLY_TEXTURE;         }

def p_apply_8(p):
    '''apply : PHOTON '''
    # { $$ = miAPPLY_PHOTON;          }

def p_apply_9(p):
    '''apply : GEOMETRY '''
    # { $$ = miAPPLY_GEOMETRY;        }

def p_apply_10(p):
    '''apply : DISPLACE '''
    # { $$ = miAPPLY_DISPLACE;        }

def p_apply_11(p):
    '''apply : EMITTER '''
    # { $$ = miAPPLY_PHOTON_EMITTER;  }

def p_apply_12(p):
    '''apply : OUTPUT '''
    # { $$ = miAPPLY_OUTPUT;          }

def p_apply_13(p):
    '''apply : LIGHTMAP '''
    # { $$ = miAPPLY_LIGHTMAP;        }

def p_apply_14(p):
    '''apply : PHOTONVOL '''
    # { $$ = miAPPLY_PHOTONVOL;       }

def p_apply_15(p):
    '''apply : STATE '''
    # { $$ = miAPPLY_STATE;           }

def p_opt_function_list_1(p):
    '''opt_function_list :  '''
    # { $$ = 0; }

def p_opt_function_list_2(p):
    '''opt_function_list : function_list '''
    # { $$ = $1; }
    p[0] = p[1]

def p_function_list_1(p):
    '''function_list : _embed0_function_list func_list '''
    # { $$ = funclist; }
    p[0] = p[2]
    
def p__embed0_function_list(p):
    '''_embed0_function_list : '''
    # { funclist = miNULLTAG; }

def p_func_list_1(p):
    '''func_list : function '''
    # { funclist = $1; }
    p[0] = [p[1]]
    
def p_func_list_2(p):
    '''func_list : func_list function '''
    # { funclist = mi_api_function_append(funclist, $2); }
    p[0] = p[1] + [p[2]]

def p_function_array_1(p):
    '''function_array : '[' ']' '''
    # { $$ = miNULLTAG; }

def p_function_array_2(p):
    '''function_array : '[' _embed0_function_array func_array ']' '''
    # { $$ = funclist; }

def p__embed0_function_array(p):
    '''_embed0_function_array : '''
    # { funclist = miNULLTAG; }

def p_func_array_1(p):
    '''func_array : function '''
    # { funclist = $1; }

def p_func_array_2(p):
    '''func_array : func_array ',' function '''
    # { funclist = mi_api_function_append(funclist, $3); }


  
def p_function_1(p):
    '''function : T_STRING _embed0_function parameter_list '''
    # { $$ = mi_api_function_call_end(functag); functag = 0;}
    
    p[0] = NamedEntity('function', '', p[1], p[3] )

def p_function_2(p):
    '''function : '=' symbol '''
    # { $$ = mi_api_function_assign($2); }

def p_function_3(p):
    '''function : '=' opt_incremental SHADER symbol function '''
    # { mi_api_shader_add($4, $5); $$ = $5;
    #                           mi_api_incremental(is_incremental);
    #                           mi_api_private(session_depth); }

def p__embed0_function(p):
    '''_embed0_function : '''
    # { mi_api_function_call($1); }

def p_opt_incremental_1(p):
    '''opt_incremental :  '''
    # { mi_api_incremental(miFALSE); }

def p_opt_incremental_2(p):
    '''opt_incremental : INCREMENTAL '''
    # { mi_api_incremental(miTRUE); }

def p_parameter_list_1(p):
    '''parameter_list : '(' ')' '''
    p[0] = []
    
def p_parameter_list_2(p):
    '''parameter_list : '(' parameter_seq ')' '''
    p[0] = p[2]
    
def p_parameter_list_3(p):
    '''parameter_list : '(' parameter_seq ',' ')' '''
    p[0] = p[2]
    
def p_parameter_seq_1(p):
    '''parameter_seq : parameter '''
    p[0] = [p[1]]
    
def p_parameter_seq_2(p):
    '''parameter_seq : parameter_seq ',' parameter '''
    p[0] = p[1] + [p[3]]
    
def p_parameter_1(p):
    '''parameter : symbol _embed0_parameter colorspace_set value_list '''
    # { mi_api_parameter_colorprofile($3); }
    # NAME PAIR
    value_list = p[4]
    if value_list and len(value_list) == 1:
        value_list = value_list[0]
    p[0] = ( p[1], value_list )
    
def p__embed0_parameter(p):
    '''_embed0_parameter : '''
    # { mi_api_parameter_name($1); }

def p_value_list_1(p):
    '''value_list : value '''
    p[0] = [p[1]]
    
def p_value_list_2(p):
    '''value_list : value_list value '''
    p[0] = p[1] + [p[2]]
    
def p_value_1(p):
    '''value : NULL '''
    p[0] = p[1]

def p_value_2(p):
    '''value : boolean '''
    # { int value = $1;
    #                           mi_api_parameter_value(miTYPE_BOOLEAN, &value,0,0); }
    p[0] = p[1]

def p_value_3(p):
    '''value : T_INTEGER '''
    # { int value = $1;
    #                           mi_api_parameter_value(miTYPE_INTEGER, &value,0,0); }
    p[0] = p[1]

def p_value_4(p):
    '''value : T_FLOAT '''
    # { float value = $1;
    #                           mi_api_parameter_value(miTYPE_SCALAR,  &value,0,0); }
    p[0] = p[1]

def p_value_5(p):
    '''value : symbol '''
    # { mi_api_parameter_value(miTYPE_STRING,  $1, 0, 0); }
    p[0] = p[1]

def p_value_6(p):
    '''value : '=' symbol '''
    # { mi_api_parameter_shader($2); }
    p[0] = p[1]

def p_value_7(p):
    '''value : '=' INTERFACE symbol '''
    # { mi_api_parameter_interface($3); }
    p[0] = p[1]

def p_value_8(p):
    '''value : '{' _embed0_value parameter_seq '}' '''
    # { mi_api_parameter_pop(); }

def p_value_9(p):
    '''value : '[' _embed1_value array_value_seq ']' '''
    # { mi_api_parameter_pop(); }

def p_value_10(p):
    '''value : '[' ']' '''
    # { mi_api_parameter_push(miTRUE);
    #                           mi_api_parameter_pop(); }

def p__embed0_value(p):
    '''_embed0_value : '''
    # { mi_api_parameter_push(miFALSE); }

def p__embed1_value(p):
    '''_embed1_value : '''
    # { mi_api_parameter_push(miTRUE); }

def p_array_value_seq_1(p):
    '''array_value_seq : _embed0_array_value_seq value_list array_value_cont '''

def p__embed0_array_value_seq(p):
    '''_embed0_array_value_seq : '''
    # { mi_api_new_array_element(); }

def p_array_value_cont_1(p):
    '''array_value_cont :  '''

def p_array_value_cont_2(p):
    '''array_value_cont : ',' _embed0_array_value_cont value_list array_value_cont '''

def p__embed0_array_value_cont(p):
    '''_embed0_array_value_cont : '''
    # { mi_api_new_array_element(); }

def p_userdata_1(p):
    '''userdata : DATA symbol data_label T_INTEGER _embed0_userdata '[' data_bytes_list ']' '''
    # { mi_api_data_end(); }

def p_userdata_2(p):
    '''userdata : DATA symbol data_label symbol '''
    # { curr_data = mi_api_data_begin($2, 1,
    #                                                         (void *)(miIntptr)$4);
    #                           curr_data->label = label;
    #                           mi_api_data_end(); }

def p_userdata_3(p):
    '''userdata : DATA symbol data_label symbol '(' _embed1_userdata parameter_seq comma_rparen '''
    # { tag = mi_api_function_call_end(0);
    #                           curr_data = mi_api_data_begin($2, 2,
    #                                                         (void *)(miIntptr)tag);
    #                           curr_data->label = label;
    #                           mi_api_data_end(); }

def p__embed0_userdata(p):
    '''_embed0_userdata : '''
    # { curr_data = mi_api_data_begin($2, 0,
    #                                                         (void *)(miIntptr)$4);
    #                           curr_data->label = label; }

def p__embed1_userdata(p):
    '''_embed1_userdata : '''
    # { mi_api_function_call($4); }

def p_data_label_1(p):
    '''data_label :  '''
    # { label = 0; }

def p_data_label_2(p):
    '''data_label : TAG T_INTEGER '''
    # { label = $2; }

def p_data_bytes_list_1(p):
    '''data_bytes_list :  '''

def p_data_bytes_list_2(p):
    '''data_bytes_list : data_bytes_list T_BYTE_STRING '''
    # { mi_api_data_byte_copy($2.len, $2.bytes); }

def p_data_decl_1(p):
    '''data_decl : DATA T_STRING parm_decl_list _embed0_data_decl data_decl_req END DECLARE '''
    # { if (curr_decl) mi_api_funcdecl_end(); }

def p__embed0_data_decl(p):
    '''_embed0_data_decl : '''
    # { if (curr_decl = mi_api_funcdecl_begin(0, $2, $3))
    #                                 curr_decl->type = miFUNCTION_DATA; }

def p_data_decl_req_1(p):
    '''data_decl_req :  '''

def p_data_decl_req_2(p):
    '''data_decl_req : gui '''

def p_data_decl_req_3(p):
    '''data_decl_req : VERSION T_INTEGER '''
    # { if (curr_decl) curr_decl->version = $2; }

def p_data_decl_req_4(p):
    '''data_decl_req : APPLY apply_list '''
    # { if (curr_decl) curr_decl->apply = $2; }

def p_data_1(p):
    '''data : DATA symbol '''
    # { *curr_datatag = mi_api_data_append(*curr_datatag,
    #                                                 mi_api_data_lookup($2)); }

def p_data_2(p):
    '''data : DATA NULL '''
    # { *curr_datatag = 0; }

def p_phenomenon_decl_1(p):
    '''phenomenon_decl : PHENOMENON shret_type T_STRING parm_decl_list _embed0_phenomenon_decl phen_body_list END DECLARE '''
    # { mi_api_phen_end(); }

def p__embed0_phenomenon_decl(p):
    '''_embed0_phenomenon_decl : '''
    # { curr_decl = mi_api_phen_begin($2, $3, $4);
    #                           if (!curr_decl) {
    #                                   memset(&dummy_decl, 0, sizeof(dummy_decl));
    #                                   curr_decl = &dummy_decl;
    #                           } }

def p_phen_body_list_1(p):
    '''phen_body_list :  '''

def p_phen_body_list_2(p):
    '''phen_body_list : phen_body_list phen_body '''

def p_phen_body_1(p):
    '''phen_body : SHADER symbol function_list '''
    # { mi_api_shader_add($2, $3); }

def p_phen_body_2(p):
    '''phen_body : material '''

def p_phen_body_3(p):
    '''phen_body : light '''

def p_phen_body_4(p):
    '''phen_body : instance '''

def p_phen_body_5(p):
    '''phen_body : declare_req '''

def p_phen_body_6(p):
    '''phen_body : ROOT phen_root '''
    # { if (curr_decl->phen.root)
    #                                 mi_api_error("multiple roots not allowed");
    #                           else
    #                                 curr_decl->phen.root = $2; }

def p_phen_body_7(p):
    '''phen_body : OUTPUT function '''
    # { curr_decl->phen.output = mi_api_function_append(
    #                                 curr_decl->phen.output,
    #                                 mi_api_output_function_def(0, 0, $2)); }

def p_phen_body_8(p):
    '''phen_body : OUTPUT T_STRING function '''
    # { mi_api_output_type_identify(&tbm, &ibm, $2);
    #                           curr_decl->phen.output = mi_api_function_append(
    #                                 curr_decl->phen.output,
    #                                 mi_api_output_function_def(tbm, ibm, $3)); }

def p_phen_body_9(p):
    '''phen_body : LENS function_list '''
    # { curr_decl->phen.lens = mi_api_function_append(
    #                                                 curr_decl->phen.lens, $2); }

def p_phen_body_10(p):
    '''phen_body : VOLUME function_list '''
    # { curr_decl->phen.volume = mi_api_function_append(
    #                                                 curr_decl->phen.volume, $2); }

def p_phen_body_11(p):
    '''phen_body : ENVIRONMENT function_list '''
    # { curr_decl->phen.environment = mi_api_function_append(
    #                                            curr_decl->phen.environment, $2); }

def p_phen_body_12(p):
    '''phen_body : GEOMETRY function_list '''
    # { curr_decl->phen.geometry = mi_api_function_append(
    #                                                 curr_decl->phen.geometry, $2);}

def p_phen_body_13(p):
    '''phen_body : CONTOUR STORE function '''
    # { curr_decl->phen.contour_store = $3; }

def p_phen_body_14(p):
    '''phen_body : CONTOUR CONTRAST function '''
    # { curr_decl->phen.contour_contrast = $3; }

def p_phen_body_15(p):
    '''phen_body : OUTPUT PRIORITY T_INTEGER '''
    # { curr_decl->phen.output_seqnr = $3; }

def p_phen_body_16(p):
    '''phen_body : LENS PRIORITY T_INTEGER '''
    # { curr_decl->phen.lens_seqnr = $3; }

def p_phen_body_17(p):
    '''phen_body : VOLUME PRIORITY T_INTEGER '''
    # { curr_decl->phen.volume_seqnr = $3; }

def p_phen_root_1(p):
    '''phen_root : MATERIAL symbol '''
    # { if (*curr_decl->declaration != 'm') {
    #                                 mi_api_error("not a material phenomenon");
    #                                 $$ = 0;
    #                           } else
    #                                 $$ = mi_api_material_lookup($2); }

def p_phen_root_2(p):
    '''phen_root : LIGHT symbol '''
    # { if (*curr_decl->declaration != 'l') {
    #                                 mi_api_error("not a light phenomenon");
    #                                 $$ = 0;
    #                           } else
    #                                 $$ = mi_api_light_lookup($2); }

def p_phen_root_3(p):
    '''phen_root : function_list '''
    # { $$ = 0;
    #                           if (*curr_decl->declaration == 'm')
    #                                 mi_api_error("must use ``root material''");
    #                           else if (*curr_decl->declaration == 'l')
    #                                 mi_api_error("must use ``root light''");
    #                           else
    #                                 $$ = mi_api_function_append(
    #                                                 curr_decl->phen.root, $1); }

def p_texture_1(p):
    '''texture : _embed0_texture tex_flags tex_type TEXTURE symbol colorspace_set _embed1_texture tex_data '''
    # { if (pyramid_filter > 0. && functag &&
    #                               (mi_db_type(functag) != miSCENE_IMAGE)) {
    #                                 mi_api_nwarning(42, "cannot filter shaders");
    #                           }
    #                           mi_api_texture_end();
    #                           functag = 0; }

def p__embed0_texture(p):
    '''_embed0_texture : '''
    # { pyramid_filter = 0.; 
    #                           curr_cprof = 0; }

def p__embed1_texture(p):
    '''_embed1_texture : '''
    # { functag = mi_api_texture_begin($5, $3, $2);
    #                           mi_api_texture_set_colorprofile($6);
    #                           mi_api_texture_set_filter(pyramid_filter); }

def p_tex_flags_1(p):
    '''tex_flags :  '''
    # { $$ = 0; }

def p_tex_flags_2(p):
    '''tex_flags : tex_flag tex_flags '''
    # { $$ = $1 | $2; }

def p_tex_flag_1(p):
    '''tex_flag : LOCAL '''
    # { $$ = 1; }

def p_tex_flag_2(p):
    '''tex_flag : FILTER '''
    # { pyramid_filter = 1.; $$ = 2; }

def p_tex_flag_3(p):
    '''tex_flag : FILTER floating '''
    # { pyramid_filter = $2;
    #                           $$ = (pyramid_filter > 0.) ? 2 : 0; }

def p_tex_flag_4(p):
    '''tex_flag : WRITABLE '''
    # { $$ = 4; }

def p_tex_type_1(p):
    '''tex_type : COLOR '''
    # { $$ = 0; }

def p_tex_type_2(p):
    '''tex_type : SCALAR '''
    # { $$ = 1; }

def p_tex_type_3(p):
    '''tex_type : VECTOR '''
    # { $$ = 2; }

def p_tex_data_1(p):
    '''tex_data : '[' T_INTEGER T_INTEGER ']' _embed0_tex_data tex_bytes_list '''
    # { functag = mi_api_texture_array_def_end(); }

def p_tex_data_2(p):
    '''tex_data : '[' T_INTEGER T_INTEGER T_INTEGER ']' _embed1_tex_data tex_bytes_list '''
    # { functag = mi_api_texture_array_def_end(); }

def p_tex_data_3(p):
    '''tex_data : tex_func_list '''
    # { functag = mi_api_texture_function_def($1); }

def p_tex_data_4(p):
    '''tex_data : T_STRING '''
    # { functag = mi_api_texture_file_def($1); }

def p_tex_data_5(p):
    '''tex_data : T_STRING '[' T_INTEGER T_INTEGER ']' '''
    # { mi_api_texture_file_size($3, $4, 1, miIMG_TYPE_ANY);
    #                           functag = mi_api_texture_file_def($1); }

def p_tex_data_6(p):
    '''tex_data : T_STRING '[' T_INTEGER T_INTEGER T_INTEGER ']' '''
    # { mi_api_texture_file_size($3, $4, $5, miIMG_TYPE_ANY);
    #                           functag = mi_api_texture_file_def($1); }

def p_tex_data_7(p):
    '''tex_data : T_STRING T_STRING '[' T_INTEGER T_INTEGER ']' '''
    # { mi_api_texture_file_size($4, $5, 0, 
    #                                         mi_api_texture_type_identify($2));
    #                           functag = mi_api_texture_file_def($1); }

def p_tex_data_8(p):
    '''tex_data : T_STRING T_STRING T_STRING '[' T_INTEGER T_INTEGER ']' '''
    # { mi_api_texture_file_size($5, $6, 0,
    #                                         mi_api_texture_type_identify($2));
    #                           functag = mi_api_texture_fileext_def($1, $3); }

def p__embed0_tex_data(p):
    '''_embed0_tex_data : '''
    # { mi_api_texture_array_def_begin($2, $3, 1); }

def p__embed1_tex_data(p):
    '''_embed1_tex_data : '''
    # { mi_api_texture_array_def_begin($2, $3, $4); }

def p_tex_func_list_1(p):
    '''tex_func_list : function '''
    # { $$ = $1; }

def p_tex_func_list_2(p):
    '''tex_func_list : function tex_func_list '''
    # { $$ = mi_api_function_append($1, $2); }

def p_tex_bytes_list_1(p):
    '''tex_bytes_list :  '''

def p_tex_bytes_list_2(p):
    '''tex_bytes_list : tex_bytes_list T_BYTE_STRING '''
    # { mi_api_texture_byte_copy($2.len, $2.bytes); }

def p_profile_data_1(p):
    '''profile_data : LIGHTPROFILE symbol _embed0_profile_data lprof_ops END LIGHTPROFILE '''
    # { mi_api_lightprofile_end(); }

def p__embed0_profile_data(p):
    '''_embed0_profile_data : '''
    # { lprof = mi_api_lightprofile_begin($2); }

def p_lprof_ops_1(p):
    '''lprof_ops : lprof_ops lprof_op '''

def p_lprof_ops_2(p):
    '''lprof_ops :  '''

def p_lprof_op_1(p):
    '''lprof_op : FORMAT IES '''
    # { lprof->format = miLP_STD_IES; }

def p_lprof_op_2(p):
    '''lprof_op : FORMAT EULUMDAT '''
    # { lprof->format = miLP_STD_EULUMDAT; }

def p_lprof_op_3(p):
    '''lprof_op : FLAGS T_INTEGER '''
    # { lprof->flags = $2; }

def p_lprof_op_4(p):
    '''lprof_op : FILE T_STRING '''
    # { char* fn = (char*) mi_scene_create(&lprof->filename,
    #                                         miSCENE_STRING, strlen($2)+1);
    #                           strcpy(fn, $2);
    #                           mi_api_release($2);
    #                           mi_scene_edit_end(lprof->filename); }

def p_lprof_op_5(p):
    '''lprof_op : HERMITE T_INTEGER '''
    # { lprof->base    = miLP_BASIS_HERMITE;
    #                           lprof->quality = $2; }

def p_lprof_op_6(p):
    '''lprof_op : RESOLUTION T_INTEGER T_INTEGER '''
    # { lprof->n_horz_angles = $2;
    #                           lprof->n_vert_angles = $3; }

def p_cprof_1(p):
    '''cprof : COLORPROFILE symbol _embed0_cprof cprof_ops END COLORPROFILE '''
    # { mi_api_colorprofile_end(); }

def p__embed0_cprof(p):
    '''_embed0_cprof : '''
    # { cprof = mi_api_colorprofile_begin($2); }

def p_cprof_ops_1(p):
    '''cprof_ops : cprof_ops cprof_op '''

def p_cprof_ops_2(p):
    '''cprof_ops :  '''

def p_cprof_op_1(p):
    '''cprof_op : COLOR SPACE T_STRING '''
    # { cprof->space = mi_api_colorprofile_space($3); }

def p_cprof_op_2(p):
    '''cprof_op : TRANSFORM floating floating floating floating floating floating floating floating floating '''
    # {
    #                            if((cprof->space & miCPROF_SPACEMASK )
    #                                                         == miCPROF_CUSTOM) { 
    #                                 miMatrix mat;
    #                                 cprof->space |= miCPROF_CID_NOT_ENOUGH;
    #                                 mat[0]  = $2;  
    #                                 mat[1]  = $3;   
    #                                 mat[2]  = $4;
    #                                 mat[3]  = 0;
    # 
    #                                 mat[4]  = $5;  
    #                                 mat[5]  = $6;   
    #                                 mat[6]  = $7;
    #                                 mat[7]  = 0;
    #                 
    #                                 mat[8]  = $8;  
    #                                 mat[9]  = $9;  
    #                                 mat[10] = $10; 
    #                                 mat[11] = 0;
    # 
    #                                 mat[12] = 0;
    #                                 mat[13] = 0;
    #                                 mat[14] = 0;
    #                                 mat[15] = 1;
    # 
    #                                 mi_api_colorprofile_custom(cprof, mat);
    #                            }
    #                         }

def p_cprof_op_3(p):
    '''cprof_op : SPECTRUM '''
    # { cprof->space = miCPROF_SPECTRUM;
    #                           mi_api_colorprofile_gamma(0.0f, 0.0f, miFALSE);  }

def p_cprof_op_4(p):
    '''cprof_op : WHITE floating floating '''
    # { /* white point chroma (x,y), intensity 1 lumen */ 
    #                           cprof->white_adapt = miTRUE;
    #                           cprof->white.r = $2/$3;
    #                           cprof->white.g = 1.0f;
    #                           cprof->white.b = (1.0f-$2-$3)/$3;
    #                           mi_colorprofile_ciexyz_to_internal(&cprof->white); }

def p_cprof_op_5(p):
    '''cprof_op : WHITE floating floating floating '''
    # { /* CIE XYZ coords of the white point */
    #                           cprof->white_adapt = miTRUE;
    #                           cprof->white.r = $2;
    #                           cprof->white.g = $3; 
    #                           cprof->white.b = $4; 
    #                           mi_colorprofile_ciexyz_to_internal(&cprof->white); }

def p_cprof_op_6(p):
    '''cprof_op : WHITE D T_INTEGER '''
    # { cprof->white_adapt = miTRUE; 
    #                           mi_api_colorprofile_white(&cprof->white, $3, 1.0f); }

def p_cprof_op_7(p):
    '''cprof_op : WHITE D T_INTEGER floating '''
    # { cprof->white_adapt = miTRUE;
    #                           mi_api_colorprofile_white(&cprof->white, $3, $4); }

def p_cprof_op_8(p):
    '''cprof_op : WHITE boolean '''
    # { cprof->white_adapt = $2; }

def p_cprof_op_9(p):
    '''cprof_op : GAMMA floating '''
    # { mi_api_colorprofile_gamma($2, 0, miFALSE); }

def p_cprof_op_10(p):
    '''cprof_op : GAMMA floating floating '''
    # { mi_api_colorprofile_gamma($2, $3, miFALSE); }

def p_cprof_op_11(p):
    '''cprof_op : GAMMA floating floating boolean '''
    # { mi_api_colorprofile_gamma($2, $3, $4); }

def p_spectrum_data_1(p):
    '''spectrum_data : SPECTRUM symbol _embed0_spectrum_data spectrum_scalars END SPECTRUM '''
    # { mi_api_spectrum_end(); }

def p__embed0_spectrum_data(p):
    '''_embed0_spectrum_data : '''
    # { mi_api_spectrum_begin($2); }

def p_spectrum_scalars_1(p):
    '''spectrum_scalars :  '''

def p_spectrum_scalars_2(p):
    '''spectrum_scalars : spectrum_scalars floating floating '''
    # {  mi_api_spectrum_pair_add($2, $3); }


#======================================
# miLight : light
#======================================
#
#    light "light_name"
#        shader_list
#        [ emitter shader_list ]
#        [ area_light_primitive ]  
#        [ origin x y z ]
#        [ direction dx dy dz ]
#        [ spread spread ]
#        [ visible ]
#        [ tag labelint ]
#        [ data ["data_name"|null] ]
#
#        [ energy r g b ]
#        [ exponent exp ]
#        [ caustic photons storeint [emitint] ]
#        [ globillum photons storeint [emitint] ]
#
#        [ shadowmap [on|off] ]
#        [ shadowmap [detail] ]
#        [ shadowmap resolution resint ]
#        [ shadowmap detail samples numint ]
#        [ shadowmap samples numint ]
#        [ shadowmap softness size ]
#        [ shadowmap file "filename" ]
#        [ shadowmap camera "cameraname" ]
#        [ shadowmap bias bias ]
#        [ shadowmap accuracy epsilon ]
#        [ shadowmap [color|alpha] ]
#    end light


def p_light_1(p):
    '''light : LIGHT symbol _embed0_light light_ops END LIGHT '''
    # { /* 0x26 equals 100110 in binary. We want to select
    #                            * only the bits that identify the light type, that
    #                            * is, the bits that tell whether we have an origin,
    #                            * a direction and a spread value.
    #                            */
    #                           switch (light_map & 0x26) {
    #                             case 0:  /* if nothing is defined, default to
    #                                       * a point light
    #                                       */
    #                             case 2:  /* origin only: point light */
    #                                     curr_light->type = miLIGHT_ORIGIN;
    #                                     break;
    #                             case 4:  /* direction only: directional light */
    #                                     curr_light->type = miLIGHT_DIRECTION;
    #                                     break;
    #                             case 6:  /* origin and direction, no spread:
    #                                       * directional light with origin
    #                                       */
    #                                     curr_light->type = miLIGHT_DIRECTION;
    #                                     curr_light->dirlight_has_org = miTRUE;
    #                                     break;
    #                             case 32: /* spread only: point light */
    #                             case 34: /* origin and spread, no direction:
    #                                       * point light
    #                                       */
    #                                     curr_light->type = miLIGHT_ORIGIN;
    #                                     break;
    #                             case 36: /* direction and spread, no origin:
    #                                       * directional light
    #                                       */
    #                                     curr_light->type = miLIGHT_DIRECTION;
    #                                     break;
    #                             case 38: /* origin, direction and spread:
    #                                       * spot light
    #                                       */
    #                                     curr_light->type = miLIGHT_SPOT;
    #                                     break;
    #                           }
    #                           mi_api_light_end(); }

def p__embed0_light(p):
    '''_embed0_light : '''
    # { curr_light = mi_api_light_begin($2);
    #                           light_map = 0; }

def p_light_ops_1(p):
    '''light_ops :  '''

def p_light_ops_2(p):
    '''light_ops : light_op light_ops '''

def p_light_op_1(p):
    '''light_op : function '''
    # { if (!(light_map & 1))
    #                                 mi_api_function_delete(&curr_light->shader);
    #                           light_map |= 1;
    #                           curr_light->shader = mi_api_function_append(
    #                                                 curr_light->shader, $1); }

def p_light_op_2(p):
    '''light_op : EMITTER function '''
    # { if (!(light_map & 8))
    #                                 mi_api_function_delete(&curr_light->emitter);
    #                           light_map |= 8;
    #                           curr_light->emitter = mi_api_function_append(
    #                                                 curr_light->emitter, $2); }

def p_light_op_3(p):
    '''light_op : HARDWARE function '''
    # { if (!(light_map & 16))
    #                                 mi_api_function_delete(&curr_light->hardware);
    #                           light_map |= 16;
    #                           curr_light->hardware = mi_api_function_append(
    #                                                 curr_light->hardware, $2); }

def p_light_op_4(p):
    '''light_op : SHADOWMAP '''
    # { curr_light->use_shadow_maps = miTRUE;
    #                           curr_light->shadowmap_flags = 0; }

def p_light_op_5(p):
    '''light_op : SHADOWMAP DETAIL '''
    # { curr_light->use_shadow_maps = miTRUE;
    #                           curr_light->shadowmap_flags |= miSHADOWMAP_DETAIL; }

def p_light_op_6(p):
    '''light_op : SHADOWMAP DETAIL SAMPLES T_INTEGER '''
    # { curr_light->shmap.samples = $4; }

def p_light_op_7(p):
    '''light_op : SHADOWMAP MERGE '''
    # { curr_light->shadowmap_flags |= miSHADOWMAP_MERGE; }

def p_light_op_8(p):
    '''light_op : SHADOWMAP MERGE boolean '''
    # { if ($3)
    #                               curr_light->shadowmap_flags |= miSHADOWMAP_MERGE;
    #                           else
    #                               curr_light->shadowmap_flags &=~miSHADOWMAP_MERGE;
    #                           }

def p_light_op_9(p):
    '''light_op : SHADOWMAP TRACE '''
    # { curr_light->shadowmap_flags |= miSHADOWMAP_TRACE; }

def p_light_op_10(p):
    '''light_op : SHADOWMAP TRACE boolean '''
    # { if ($3)
    #                               curr_light->shadowmap_flags |= miSHADOWMAP_TRACE;
    #                           else
    #                               curr_light->shadowmap_flags &=~miSHADOWMAP_TRACE;
    #                           }

def p_light_op_11(p):
    '''light_op : SHADOWMAP WINDOW floating floating floating floating '''
    # { curr_light->shadowmap_flags |= miSHADOWMAP_CROP;
    #                           curr_light->shmap_h_min =
    #                                                 (short)miFLOOR($3 * SHRT_MAX);
    #                           curr_light->shmap_v_min =
    #                                                 (short)miFLOOR($4 * SHRT_MAX);
    #                           curr_light->shmap_h_max =
    #                                                 (short)miFLOOR($5 * SHRT_MAX);
    #                           curr_light->shmap_v_max =
    #                                                 (short)miFLOOR($6 * SHRT_MAX);}

def p_light_op_12(p):
    '''light_op : SHADOWMAP boolean '''
    # { curr_light->use_shadow_maps = $2;
    #                           curr_light->shadowmap_flags = 0; }

def p_light_op_13(p):
    '''light_op : SHADOWMAP CAMERA symbol '''
    # { mi_api_light_shmap_camera($3); }

def p_light_op_14(p):
    '''light_op : SHADOWMAP BIAS floating '''
    # { curr_light->shadowmap_bias = $3; }
    
def p_light_op_15(p):
    '''light_op : ORIGIN vector '''
    # { curr_light->origin = $2;
    #                           light_map |= 2; }

def p_light_op_16(p):
    '''light_op : DIRECTION vector '''
    # { curr_light->direction = $2;
    #                           mi_vector_normalize(&curr_light->direction);
    #                           light_map |= 4; }

def p_light_op_17(p):
    '''light_op : ENERGY colorspace_set color '''
    # { mi_api_colorprofile_to_renderspace(
    #                                             &$3, $2, $3.r, $3.g, $3.b);
    #                           curr_light->energy = $3; }

def p_light_op_18(p):
    '''light_op : ENERGY SPECTRUM symbol '''
    # { curr_light->emitter_spectrum 
    #                                       = mi_api_name_lookup($3);}

def p_light_op_19(p):
    '''light_op : EXPONENT floating '''
    # { curr_light->exponent = $2; }

def p_light_op_20(p):
    '''light_op : CAUSTIC PHOTONS T_INTEGER '''
    # { curr_light->caustic_store_photons = $3;
    #                           curr_light->caustic_emit_photons = 0; }

def p_light_op_21(p):
    '''light_op : CAUSTIC PHOTONS T_INTEGER T_INTEGER '''
    # { curr_light->caustic_store_photons = $3;
    #                           curr_light->caustic_emit_photons = $4; }

def p_light_op_22(p):
    '''light_op : GLOBILLUM PHOTONS T_INTEGER '''
    # { curr_light->global_store_photons = $3;
    #                           curr_light->global_emit_photons = 0; }

def p_light_op_23(p):
    '''light_op : GLOBILLUM PHOTONS T_INTEGER T_INTEGER '''
    # { curr_light->global_store_photons = $3;
    #                           curr_light->global_emit_photons = $4; }

def p_light_op_24(p):
    '''light_op : PHOTONS ONLY boolean '''
    # { curr_light->photons_only = $3; }

def p_light_op_25(p):
    '''light_op : RECTANGLE vector vector light_samples '''
    # { curr_light->area = miLIGHT_RECTANGLE;
    #                           curr_light->primitive.rectangle.edge_u = $2;
    #                           curr_light->primitive.rectangle.edge_v = $3; }

def p_light_op_26(p):
    '''light_op : DISC vector floating light_samples '''
    # { curr_light->area = miLIGHT_DISC;
    #                           curr_light->primitive.disc.normal      = $2;
    #                           curr_light->primitive.disc.radius      = $3; }

def p_light_op_27(p):
    '''light_op : SPHERE floating light_samples '''
    # { curr_light->area = miLIGHT_SPHERE;
    #                           curr_light->primitive.sphere.radius    = $2; }

def p_light_op_28(p):
    '''light_op : CYLINDER vector floating light_samples '''
    # { curr_light->area = miLIGHT_CYLINDER;
    #                           curr_light->primitive.cylinder.axis    = $2;
    #                           curr_light->primitive.cylinder.radius  = $3; }

def p_light_op_29(p):
    '''light_op : OBJECT symbol light_samples '''
    # { curr_light->area = miLIGHT_OBJECT;
    #                           curr_light->primitive.object.object =
    #                                 mi_api_name_lookup($2); }

def p_light_op_30(p):
    '''light_op : USER light_samples '''
    # { curr_light->area = miLIGHT_USER; }

def p_light_op_31(p):
    '''light_op : RECTANGLE '''
    # { curr_light->area = miLIGHT_NONE; }

def p_light_op_32(p):
    '''light_op : DISC '''
    # { curr_light->area = miLIGHT_NONE; }

def p_light_op_33(p):
    '''light_op : SPHERE '''
    # { curr_light->area = miLIGHT_NONE; }

def p_light_op_34(p):
    '''light_op : CYLINDER '''
    # { curr_light->area = miLIGHT_NONE; }

def p_light_op_35(p):
    '''light_op : SPREAD floating '''
    # { curr_light->spread = $2;
    #                           light_map |= 32; }

def p_light_op_36(p):
    '''light_op : SHADOWMAP RESOLUTION T_INTEGER '''
    # { curr_light->shadowmap_resolution = $3; }

def p_light_op_37(p):
    '''light_op : SHADOWMAP SOFTNESS floating '''
    # { curr_light->shadowmap_softness = $3; }

def p_light_op_38(p):
    '''light_op : SHADOWMAP SAMPLES T_INTEGER '''
    # { curr_light->shadowmap_samples = $3; }

def p_light_op_39(p):
    '''light_op : SHADOWMAP FILTER filter_type '''
    # { curr_light->shmap.filter   = $3;
    #                           curr_light->shmap.filter_u =
    #                           curr_light->shmap.filter_v = 0.0; }

def p_light_op_40(p):
    '''light_op : SHADOWMAP FILTER filter_type floating '''
    # { curr_light->shmap.filter   = $3;
    #                           curr_light->shmap.filter_u =
    #                           curr_light->shmap.filter_v = $4; }

def p_light_op_41(p):
    '''light_op : SHADOWMAP FILTER filter_type floating floating '''
    # { curr_light->shmap.filter   = $3;
    #                           curr_light->shmap.filter_u = $4;
    #                           curr_light->shmap.filter_v = $5; }

def p_light_op_42(p):
    '''light_op : SHADOWMAP ACCURACY floating '''
    # { curr_light->shmap.accuracy = $3; }

def p_light_op_43(p):
    '''light_op : SHADOWMAP ALPHA '''
    # { curr_light->shmap.type = 'a'; }

def p_light_op_44(p):
    '''light_op : SHADOWMAP COLOR '''
    # { curr_light->shmap.type = 'c'; }

def p_light_op_45(p):
    '''light_op : SHADOWMAP FILE T_STRING '''
    # { mi_scene_delete(curr_light->shadowmap_file);
    #                           strcpy((char *)mi_scene_create(
    #                                         &curr_light->shadowmap_file,
    #                                         miSCENE_STRING, strlen($3)+1), $3);
    #                           mi_db_unpin(curr_light->shadowmap_file);
    #                           mi_api_release($3); }

def p_light_op_46(p):
    '''light_op : LIGHTPROFILE T_SYMBOL '''
    # {  if (strcmp($2, "Lambertian")) { 
    #                                 curr_light->lightprofile = 
    #                                     mi_api_lightprofile_lookup($2);
    #                                 if (curr_light->lightprofile) {
    #                                     curr_light->use_lprof = miTRUE;
    #                                 } 
    #                             } else {
    #                                 curr_light->use_lprof = miTRUE;
    #                             }
    #                         }

def p_light_op_47(p):
    '''light_op : VISIBLE '''
    # { curr_light->visible = miTRUE; }

def p_light_op_48(p):
    '''light_op : VISIBLE boolean '''
    # { curr_light->visible = $2; }

def p_light_op_49(p):
    '''light_op : TAG T_INTEGER '''
    # { curr_light->label = $2; }

def p_light_op_50(p):
    '''light_op : _embed0_light_op data '''

def p_light_op_51(p):
    '''light_op : dummy_attribute '''

def p__embed0_light_op(p):
    '''_embed0_light_op : '''
    # { curr_datatag = &curr_light->userdata; }

def p_light_samples_1(p):
    '''light_samples :  '''

def p_light_samples_2(p):
    '''light_samples : T_INTEGER '''
    # { curr_light->samples_u     = $1;
    #                           curr_light->samples_v     = 1;  }

def p_light_samples_3(p):
    '''light_samples : T_INTEGER T_INTEGER '''
    # { curr_light->samples_u     = $1;
    #                           curr_light->samples_v     = $2; }

def p_light_samples_4(p):
    '''light_samples : T_INTEGER T_INTEGER T_INTEGER '''
    # { curr_light->samples_u     = $1;
    #                           curr_light->samples_v     = $2;
    #                           curr_light->low_level     = $3; }

def p_light_samples_5(p):
    '''light_samples : T_INTEGER T_INTEGER T_INTEGER T_INTEGER T_INTEGER '''
    # { curr_light->samples_u     = $1;
    #                           curr_light->samples_v     = $2;
    #                           curr_light->low_level     = $3;
    #                           curr_light->low_samples_u = $4;
    #                           curr_light->low_samples_v = $5; }

#======================================
# miMaterial : material
#======================================
#
#    material "material_name"
#        [opaque]
#        shader_list
#        [ displace [shader_list] ]
#        [ shadow [shader_list] ]
#        [ volume [shader_list] ]
#        [ environment [shader_list] ]
#        [ contour [shader_list] ]
#        [ photon [shader_list] ]
#        [ photonvol [shader_list] ]
#        [ lightmap [shader_list] ]
#        [ bsdf [shader_list] ] 
#    end material

def p_material_1(p):
    '''material : MATERIAL symbol _embed0_material mtl_flags mtl_shader mtl_args END MATERIAL '''
    # { mi_api_material_end(); }
    type = p[1]
    name = p[3]
    
    #p[0] = NamedEntity( )

def p__embed0_material(p):
    '''_embed0_material : '''
    # { curr_mtl = mi_api_material_begin($2);
    #                           have_d = have_s = have_v = have_e = have_c =
    #                           have_p = have_pv = have_lm = have_hw = 0; }

def p_mtl_shader_1(p):
    '''mtl_shader :  '''

def p_mtl_shader_2(p):
    '''mtl_shader : function_list '''
    # { curr_mtl->shader = $1; }

def p_mtl_flags_1(p):
    '''mtl_flags :  '''

def p_mtl_flags_2(p):
    '''mtl_flags : mtl_flag mtl_flags '''

def p_mtl_flag_1(p):
    '''mtl_flag : NOCONTOUR '''
    # { mi_api_warning(
    #                                 "obsolete \"nocontour\" flag ignored"); }

def p_mtl_flag_2(p):
    '''mtl_flag : OPAQUE '''
    # { curr_mtl->opaque = miTRUE; }

def p_mtl_flag_3(p):
    '''mtl_flag : dummy_attribute '''

def p_mtl_args_1(p):
    '''mtl_args :  '''

def p_mtl_args_2(p):
    '''mtl_args : mtl_arg mtl_args '''

def p_mtl_arg_1(p):
    '''mtl_arg : DISPLACE '''
    # { mi_api_function_delete(&curr_mtl->displace); }

def p_mtl_arg_2(p):
    '''mtl_arg : DISPLACE _embed0_mtl_arg function_list '''
    # { curr_mtl->displace = $3; }

def p_mtl_arg_3(p):
    '''mtl_arg : SHADOW '''
    # { mi_api_function_delete(&curr_mtl->shadow); }

def p_mtl_arg_4(p):
    '''mtl_arg : SHADOW _embed1_mtl_arg function_list '''
    # {  curr_mtl->shadow = $3; }

def p_mtl_arg_5(p):
    '''mtl_arg : VOLUME '''
    # { mi_api_function_delete(&curr_mtl->volume); }

def p_mtl_arg_6(p):
    '''mtl_arg : VOLUME _embed2_mtl_arg function_list '''
    # { curr_mtl->volume = $3; }

def p_mtl_arg_7(p):
    '''mtl_arg : ENVIRONMENT '''
    # { mi_api_function_delete(&curr_mtl->environment); }

def p_mtl_arg_8(p):
    '''mtl_arg : ENVIRONMENT _embed3_mtl_arg function_list '''
    # { curr_mtl->environment = $3; }

def p_mtl_arg_9(p):
    '''mtl_arg : CONTOUR '''
    # { mi_api_function_delete(&curr_mtl->contour); }

def p_mtl_arg_10(p):
    '''mtl_arg : CONTOUR _embed4_mtl_arg function_list '''
    # { curr_mtl->contour = $3; }

def p_mtl_arg_11(p):
    '''mtl_arg : PHOTON '''
    # { mi_api_function_delete(&curr_mtl->photon); }

def p_mtl_arg_12(p):
    '''mtl_arg : PHOTON _embed5_mtl_arg function_list '''
    # { curr_mtl->photon = $3; }

def p_mtl_arg_13(p):
    '''mtl_arg : PHOTONVOL '''
    # { mi_api_function_delete(&curr_mtl->photonvol); }

def p_mtl_arg_14(p):
    '''mtl_arg : PHOTONVOL _embed6_mtl_arg function_list '''
    # { curr_mtl->photonvol = $3; }

def p_mtl_arg_15(p):
    '''mtl_arg : LIGHTMAP '''
    # { mi_api_function_delete(&curr_mtl->lightmap); }

def p_mtl_arg_16(p):
    '''mtl_arg : LIGHTMAP _embed7_mtl_arg function_list '''
    # { curr_mtl->lightmap = $3; }

def p_mtl_arg_17(p):
    '''mtl_arg : HARDWARE '''
    # { mi_api_function_delete(&curr_mtl->hardware); }

def p_mtl_arg_18(p):
    '''mtl_arg : HARDWARE _embed8_mtl_arg function_list '''
    # { curr_mtl->hardware = $3; }

def p__embed0_mtl_arg(p):
    '''_embed0_mtl_arg : '''
    # { if (!have_d++)
    #                                 mi_api_function_delete(&curr_mtl->displace); }

def p__embed1_mtl_arg(p):
    '''_embed1_mtl_arg : '''
    # { if (!have_s++)
    #                                 mi_api_function_delete(&curr_mtl->shadow); }

def p__embed2_mtl_arg(p):
    '''_embed2_mtl_arg : '''
    # { if (!have_v++) 
    #                                 mi_api_function_delete(&curr_mtl->volume); }

def p__embed3_mtl_arg(p):
    '''_embed3_mtl_arg : '''
    # { if (!have_e++)
    #                                 mi_api_function_delete(&curr_mtl->environment); }

def p__embed4_mtl_arg(p):
    '''_embed4_mtl_arg : '''
    # { if (!have_c++)
    #                                 mi_api_function_delete(&curr_mtl->contour); }

def p__embed5_mtl_arg(p):
    '''_embed5_mtl_arg : '''
    # { if (!have_p++)
    #                                 mi_api_function_delete(&curr_mtl->photon); }

def p__embed6_mtl_arg(p):
    '''_embed6_mtl_arg : '''
    # { if (!have_pv++)
    #                                 mi_api_function_delete(&curr_mtl->photonvol); }

def p__embed7_mtl_arg(p):
    '''_embed7_mtl_arg : '''
    # { if (!have_lm++)
    #                                 mi_api_function_delete(&curr_mtl->lightmap); }

def p__embed8_mtl_arg(p):
    '''_embed8_mtl_arg : '''
    # { if (!have_hw++)
    #                                 mi_api_function_delete(&curr_mtl->hardware); }

#======================================
# miObject : object
#======================================
#
#    object "object_name"
#        [ visible [on|off] ]
#        [ shadow [on|off] ]
#        [ shadow [mode] ]
#        [ shadowmap [on|off] ]
#        [ trace [on|off] ]
#        [ reflection mode ]
#        [ refraction mode ]
#        [ transparency mode ]
#        [ select [on|off] ]
#        [ tagged [on|off] ]
#        [ caustic on|off ]
#        [ globillum on|off ]
#        [ finalgather on|off ]
#        [ caustic [mode] ]
#        [ globillum [mode] ]
#        [ finalgather mode ]
#        [ finalgather file file (list) ]
#        [ face [front|back|both] ]
#        [ box [xmin ymin zmin xmax ymax zmax] ]
#        [ motion box [xmin ymin zmin xmax ymax zmax] ]
#        [ max displace value ]
#        [ ray offset value ]
#        [ samples min  max ]
#        [ shading samples samplesscalar ]
#        [ data null|"data_name" ]
#        [ tag label_numberint ]
#        [ file "file_name" ]
#        [ basis list ]
#        group
#            vector list
#            vertex list
#            geometry list
#            approximation list
#        end group
#    end object

def p_object_1(p):
    '''object : OBJECT _embed0_object opt_symbol _embed1_object obj_flags object_body END OBJECT '''
    # { mi_api_object_end(); mi_end_object(); }

def p__embed0_object(p):
    '''_embed0_object : '''
    # { mi_get_filepos(&filepos, &filename); filepos-=7; }

def p__embed1_object(p):
    '''_embed1_object : '''
    # { if (mi_reload_parsing()) {
    #                                 mi_api_incremental(miTRUE);
    #                                 curr_obj = mi_api_object_begin($3);
    #                           } else {
    #                             curr_obj = mi_api_object_begin_r(
    #                                 $3, mi_api_strdup(filename), filepos); } }

def p_obj_flags_1(p):
    '''obj_flags :  '''

def p_obj_flags_2(p):
    '''obj_flags : obj_flags obj_flag '''

def p_obj_flag_1(p):
    '''obj_flag : VISIBLE '''
    # { curr_obj->visible      = miTRUE; }

def p_obj_flag_2(p):
    '''obj_flag : VISIBLE boolean '''
    # { curr_obj->visible      = $2; }

def p_obj_flag_3(p):
    '''obj_flag : SHADOW '''
    # { curr_obj->shadow       = 0x03; }

def p_obj_flag_4(p):
    '''obj_flag : SHADOW boolean '''
    # { curr_obj->shadow       = $2 ? 0x03 : 0x02; }

def p_obj_flag_5(p):
    '''obj_flag : SHADOW T_INTEGER '''
    # { curr_obj->shadow       = ($2 & 0x03); }

def p_obj_flag_6(p):
    '''obj_flag : SHADOWMAP '''
    # { curr_obj->shadowmap    = miTRUE; }

def p_obj_flag_7(p):
    '''obj_flag : SHADOWMAP boolean '''
    # { curr_obj->shadowmap    = $2; }

def p_obj_flag_8(p):
    '''obj_flag : TRACE '''
    # { curr_obj->reflection   =
    #                           curr_obj->refraction   =
    #                           curr_obj->finalgather  = 0x03; }

def p_obj_flag_9(p):
    '''obj_flag : TRACE boolean '''
    # { curr_obj->reflection   =
    #                           curr_obj->refraction   =
    #                           curr_obj->finalgather  = $2 ? 0x03 : 0x02; }

def p_obj_flag_10(p):
    '''obj_flag : REFLECTION T_INTEGER '''
    # { curr_obj->reflection   = ($2 & 0x03); }

def p_obj_flag_11(p):
    '''obj_flag : REFRACTION T_INTEGER '''
    # { curr_obj->refraction   = ($2 & 0x03); }

def p_obj_flag_12(p):
    '''obj_flag : TRANSPARENCY T_INTEGER '''
    # { curr_obj->transparency = ($2 & 0x03); }

def p_obj_flag_13(p):
    '''obj_flag : FACE FRONT '''
    # { curr_obj->face         = 'f'; }

def p_obj_flag_14(p):
    '''obj_flag : FACE BACK '''
    # { curr_obj->face         = 'b'; }

def p_obj_flag_15(p):
    '''obj_flag : FACE BOTH '''
    # { curr_obj->face         = 'a'; }

def p_obj_flag_16(p):
    '''obj_flag : SELECT '''
    # { curr_obj->select       = miTRUE; }

def p_obj_flag_17(p):
    '''obj_flag : SELECT boolean '''
    # { curr_obj->select       = $2; }

def p_obj_flag_18(p):
    '''obj_flag : TAGGED '''
    # { curr_obj->mtl_is_label = miTRUE; }

def p_obj_flag_19(p):
    '''obj_flag : TAGGED boolean '''
    # { curr_obj->mtl_is_label = $2; }

def p_obj_flag_20(p):
    '''obj_flag : CAUSTIC '''
    # { curr_obj->caustic     |= 3; }

def p_obj_flag_21(p):
    '''obj_flag : CAUSTIC boolean '''
    # { curr_obj->caustic     &= 0x03;
    #                           if (!$2) curr_obj->caustic |= 0x10; }

def p_obj_flag_22(p):
    '''obj_flag : CAUSTIC T_INTEGER '''
    # { curr_obj->caustic     &= 0x10;
    #                           curr_obj->caustic     |= ($2 & 0x03); }

def p_obj_flag_23(p):
    '''obj_flag : GLOBILLUM '''
    # { curr_obj->globillum   |= 3; }

def p_obj_flag_24(p):
    '''obj_flag : GLOBILLUM boolean '''
    # { curr_obj->globillum   &= 0x03;
    #                           if (!$2) curr_obj->globillum |= 0x10; }

def p_obj_flag_25(p):
    '''obj_flag : GLOBILLUM T_INTEGER '''
    # { curr_obj->globillum   &= 0x10;
    #                           curr_obj->globillum   |= ($2 & 0x03); }

def p_obj_flag_26(p):
    '''obj_flag : PHOTONMAP FILE '''
    # { mi_scene_delete(curr_obj->photonmap_file);
    #                           curr_obj->photonmap_file = miNULLTAG; }

def p_obj_flag_27(p):
    '''obj_flag : PHOTONMAP FILE OFF '''
    # { mi_scene_delete(curr_obj->photonmap_file);
    #                           curr_obj->photonmap_file = miNULLTAG; }

def p_obj_flag_28(p):
    '''obj_flag : PHOTONMAP FILE T_STRING '''
    # {  mi_scene_delete(curr_obj->photonmap_file);
    #                            if (($3)[0]) {
    #                                 strcpy((char *)mi_scene_create(
    #                                         &curr_obj->photonmap_file,
    #                                         miSCENE_STRING, strlen($3)+1), $3);
    #                                 mi_scene_edit_end(curr_obj->photonmap_file);
    #                             } else {
    #                                 curr_obj->photonmap_file = miNULLTAG; 
    #                             } 
    #                            mi_api_release($3); }

def p_obj_flag_29(p):
    '''obj_flag : FINALGATHER boolean '''
    # { curr_obj->finalgather &= 0x03;
    #                           if (!$2) curr_obj->finalgather |= 0x10; }

def p_obj_flag_30(p):
    '''obj_flag : FINALGATHER T_INTEGER '''
    # { curr_obj->finalgather &= 0x10;
    #                           curr_obj->finalgather |= ($2 & 0x03); }

def p_obj_flag_31(p):
    '''obj_flag : FINALGATHER FILE map_list '''
    # { mi_api_taglist_reset(&curr_obj->finalgather_file,
    #                                                $3); }

def p_obj_flag_32(p):
    '''obj_flag : SHADING SAMPLES floating '''
    # { curr_obj->shading_samples = $3; }

def p_obj_flag_33(p):
    '''obj_flag : HARDWARE '''
    # { curr_obj->hardware = miTRUE; }

def p_obj_flag_34(p):
    '''obj_flag : HARDWARE boolean '''
    # { curr_obj->hardware = $2; }

def p_obj_flag_35(p):
    '''obj_flag : TAG T_INTEGER '''
    # { curr_obj->label = $2; }

def p_obj_flag_36(p):
    '''obj_flag : _embed0_obj_flag data '''

def p_obj_flag_37(p):
    '''obj_flag : transform '''
    # { mi_api_object_matrix($1); }

def p_obj_flag_38(p):
    '''obj_flag : MAX DISPLACE floating '''
    # { curr_obj->maxdisplace = $3; }

def p_obj_flag_39(p):
    '''obj_flag : RAY OFFSET floating '''
    # {curr_obj->ray_offset = $3; }

def p_obj_flag_40(p):
    '''obj_flag : BOX vector vector '''
    # { curr_obj->bbox_min = $2;
    #                           curr_obj->bbox_max = $3; }

def p_obj_flag_41(p):
    '''obj_flag : BOX '''
    # { curr_obj->bbox_min = nullvec;
    #                           curr_obj->bbox_max = nullvec; }

def p_obj_flag_42(p):
    '''obj_flag : MOTION BOX vector vector '''
    # { curr_obj->bbox_min_m = $3;
    #                           curr_obj->bbox_max_m = $4; }

def p_obj_flag_43(p):
    '''obj_flag : MOTION BOX '''
    # { curr_obj->bbox_min_m = nullvec;
    #                           curr_obj->bbox_max_m = nullvec; }

def p_obj_flag_44(p):
    '''obj_flag : SAMPLES T_INTEGER '''
    # { curr_obj->min_samples = $2-2;
    #                           curr_obj->max_samples = $2;}

def p_obj_flag_45(p):
    '''obj_flag : SAMPLES T_INTEGER T_INTEGER '''
    # { curr_obj->min_samples = $2;
    #                           curr_obj->max_samples = $3;}

def p_obj_flag_46(p):
    '''obj_flag : VOLUME GROUP T_INTEGER '''
    # { curr_obj->volume_id = $3; }

def p_obj_flag_47(p):
    '''obj_flag : dummy_attribute '''

def p__embed0_obj_flag(p):
    '''_embed0_obj_flag : '''
    # { curr_datatag = &curr_obj->userdata; }

def p_object_body_1(p):
    '''object_body : bases_and_groups '''

def p_object_body_2(p):
    '''object_body : FILE T_STRING '''
    # { mi_api_object_file($2); }

def p_object_body_3(p):
    '''object_body : hair_object '''

def p_object_body_4(p):
    '''object_body : trilist_object '''

def p_object_body_5(p):
    '''object_body : isect_object '''

def p_bases_and_groups_1(p):
    '''bases_and_groups :  '''

def p_bases_and_groups_2(p):
    '''bases_and_groups : basis bases_and_groups '''

def p_bases_and_groups_3(p):
    '''bases_and_groups : group bases_and_groups '''

def p_basis_1(p):
    '''basis : BASIS symbol rational MATRIX T_INTEGER T_INTEGER basis_matrix '''
    # { mi_api_basis_add($2, $3, miBASIS_MATRIX, $5,$6,$7); }

def p_basis_2(p):
    '''basis : BASIS symbol rational BEZIER T_INTEGER '''
    # { mi_api_basis_add($2, $3, miBASIS_BEZIER, $5, 0, 0); }

def p_basis_3(p):
    '''basis : BASIS symbol rational TAYLOR T_INTEGER '''
    # { mi_api_basis_add($2, $3, miBASIS_TAYLOR, $5, 0, 0); }

def p_basis_4(p):
    '''basis : BASIS symbol rational BSPLINE T_INTEGER '''
    # { mi_api_basis_add($2, $3, miBASIS_BSPLINE, $5, 0, 0);}

def p_basis_5(p):
    '''basis : BASIS symbol rational CARDINAL '''
    # { mi_api_basis_add($2, $3, miBASIS_CARDINAL, 3, 0, 0);}

def p_rational_1(p):
    '''rational :  '''
    # { $$ = miFALSE; }

def p_rational_2(p):
    '''rational : RATIONAL '''
    # { $$ = miTRUE; }

def p_basis_matrix_1(p):
    '''basis_matrix :  '''
    # { $$ = mi_api_dlist_create(miDLIST_GEOSCALAR); }

def p_basis_matrix_2(p):
    '''basis_matrix : basis_matrix floating '''
    # { miGeoScalar s=$2; mi_api_dlist_add($1, &s); $$=$1; }

def p_group_1(p):
    '''group : GROUP opt_symbol merge_option _embed0_group vector_list vertex_list geometry_list END GROUP '''
    # { mi_api_object_group_end(); }

def p__embed0_group(p):
    '''_embed0_group : '''
    # { mi_api_object_group_begin($3);
    #                           mi_api_release($2); }

def p_merge_option_1(p):
    '''merge_option :  '''
    # { $$ = 0.0; }

def p_merge_option_2(p):
    '''merge_option : MERGE floating '''
    # { $$ = $2; }

def p_vector_list_1(p):
    '''vector_list :  '''

def p_vector_list_2(p):
    '''vector_list : vector_list geovector '''
    # { mi_api_geovector_xyz_add(&$2); }

def p_vertex_list_1(p):
    '''vertex_list :  '''

def p_vertex_list_2(p):
    '''vertex_list : vertex_list vertex '''

def p_vertex_1(p):
    '''vertex : V T_INTEGER _embed0_vertex n_vector d_vector t_vector_list m_vector_list u_vector_list vertex_flag '''

def p__embed0_vertex(p):
    '''_embed0_vertex : '''
    # { mi_api_vertex_add($2); }

def p_n_vector_1(p):
    '''n_vector :  '''

def p_n_vector_2(p):
    '''n_vector : N T_INTEGER '''
    # { mi_api_vertex_normal_add($2); }

def p_d_vector_1(p):
    '''d_vector :  '''

def p_d_vector_2(p):
    '''d_vector : D T_INTEGER T_INTEGER '''
    # { mi_api_vertex_deriv_add($2, $3); }

def p_d_vector_3(p):
    '''d_vector : D T_INTEGER T_INTEGER T_INTEGER '''
    # { mi_api_vertex_deriv2_add($2, $3, $4); }

def p_d_vector_4(p):
    '''d_vector : D T_INTEGER T_INTEGER T_INTEGER T_INTEGER T_INTEGER '''
    # { mi_api_vertex_deriv_add($2, $3);
    #                           mi_api_vertex_deriv2_add($4, $5, $6); }

def p_m_vector_list_1(p):
    '''m_vector_list :  '''

def p_m_vector_list_2(p):
    '''m_vector_list : m_vector_list M T_INTEGER '''
    # { mi_api_vertex_motion_add($3); }

def p_t_vector_list_1(p):
    '''t_vector_list :  '''

def p_t_vector_list_2(p):
    '''t_vector_list : t_vector_list T T_INTEGER '''
    # { mi_api_vertex_tex_add($3, -1, -1); }

def p_t_vector_list_3(p):
    '''t_vector_list : t_vector_list T T_INTEGER T_INTEGER T_INTEGER '''
    # { mi_api_vertex_tex_add($3, $4, $5); }

def p_u_vector_list_1(p):
    '''u_vector_list :  '''

def p_u_vector_list_2(p):
    '''u_vector_list : u_vector_list U T_INTEGER '''
    # { mi_api_vertex_user_add($3); }

def p_vertex_flag_1(p):
    '''vertex_flag :  '''

def p_vertex_flag_2(p):
    '''vertex_flag : CUSP '''
    # { mi_api_vertex_flags_add(miAPI_V_CUSP, 0, 1.f); }

def p_vertex_flag_3(p):
    '''vertex_flag : CUSP LEVEL T_INTEGER '''
    # { mi_api_vertex_flags_add(miAPI_V_CUSP, $3, 1.f); }

def p_vertex_flag_4(p):
    '''vertex_flag : CONIC '''
    # { mi_api_vertex_flags_add(miAPI_V_CONIC, 0, 1.f); }

def p_vertex_flag_5(p):
    '''vertex_flag : CONIC LEVEL T_INTEGER '''
    # { mi_api_vertex_flags_add(miAPI_V_CONIC, $3, 1.f); }

def p_vertex_flag_6(p):
    '''vertex_flag : CORNER '''
    # { mi_api_vertex_flags_add(miAPI_V_CORNER, 0, 1.f); }

def p_vertex_flag_7(p):
    '''vertex_flag : CORNER LEVEL T_INTEGER '''
    # { mi_api_vertex_flags_add(miAPI_V_CORNER, $3, 1.f); }

def p_vertex_flag_8(p):
    '''vertex_flag : DART '''
    # { mi_api_vertex_flags_add(miAPI_V_DART, 0, 0.f); }

def p_geometry_list_1(p):
    '''geometry_list :  '''

def p_geometry_list_2(p):
    '''geometry_list : geometry_list geometry '''

def p_geometry_1(p):
    '''geometry : polygon '''

def p_geometry_2(p):
    '''geometry : curve '''

def p_geometry_3(p):
    '''geometry : spacecurve '''

def p_geometry_4(p):
    '''geometry : surface '''

def p_geometry_5(p):
    '''geometry : subdivsurf '''

def p_geometry_6(p):
    '''geometry : ccmesh '''

def p_geometry_7(p):
    '''geometry : connection '''

def p_geometry_8(p):
    '''geometry : approximation '''


#    c ["material_name"] vertex_ref_list  
#    cp ["material_name"] vertex_ref_list  
#    p ["material_name"] vertex_ref_list  
#    p ["material_name"] vertex_ref_list hole vertex_ref_list ...  

def p_polygon_1(p):
    '''polygon : CP opt_symbol _embed0_polygon poly_indices '''
    # { mi_api_poly_end(); }

def p_polygon_2(p):
    '''polygon : P opt_symbol _embed1_polygon poly_indices '''
    # { mi_api_poly_end(); }

def p_polygon_3(p):
    '''polygon : STRIP opt_symbol _embed2_polygon strip_indices '''
    # { mi_api_poly_end(); }

def p_polygon_4(p):
    '''polygon : FAN opt_symbol _embed3_polygon strip_indices '''
    # { mi_api_poly_end(); }

def p__embed0_polygon(p):
    '''_embed0_polygon : '''
    # { mi_api_poly_begin(1, $2); }

def p__embed1_polygon(p):
    '''_embed1_polygon : '''
    # { mi_api_poly_begin(0, $2); }

def p__embed2_polygon(p):
    '''_embed2_polygon : '''
    # { mi_api_poly_begin(2, $2); }

def p__embed3_polygon(p):
    '''_embed3_polygon : '''
    # { mi_api_poly_begin(3, $2); }

def p_poly_indices_1(p):
    '''poly_indices :  '''

def p_poly_indices_2(p):
    '''poly_indices : T_INTEGER _embed0_poly_indices poly_indices '''

def p_poly_indices_3(p):
    '''poly_indices : HOLE _embed1_poly_indices poly_indices '''

def p__embed0_poly_indices(p):
    '''_embed0_poly_indices : '''
    # { mi_api_poly_index_add($1); }

def p__embed1_poly_indices(p):
    '''_embed1_poly_indices : '''
    # { mi_api_poly_hole_add(); }

def p_strip_indices_1(p):
    '''strip_indices :  '''

def p_strip_indices_2(p):
    '''strip_indices : T_INTEGER _embed0_strip_indices strip_indices '''

def p__embed0_strip_indices(p):
    '''_embed0_strip_indices : '''
    # { mi_api_poly_index_add($1); }

def p_h_vertex_ref_seq_1(p):
    '''h_vertex_ref_seq : h_vertex_ref '''

def p_h_vertex_ref_seq_2(p):
    '''h_vertex_ref_seq : h_vertex_ref_seq h_vertex_ref '''

def p_h_vertex_ref_1(p):
    '''h_vertex_ref : T_INTEGER '''
    # { mi_api_vertex_ref_add($1, (double)1.0); }

def p_h_vertex_ref_2(p):
    '''h_vertex_ref : T_INTEGER T_FLOAT '''
    # { mi_api_vertex_ref_add($1, $2); }

def p_h_vertex_ref_3(p):
    '''h_vertex_ref : T_INTEGER W floating '''
    # { mi_api_vertex_ref_add($1, $3); }

def p_para_list_1(p):
    '''para_list : T_FLOAT '''
    # { miDlist *dlp =mi_api_dlist_create(miDLIST_GEOSCALAR);
    #                           miGeoScalar s = $1;   /* $1 is a double */
    #                           mi_api_dlist_add(dlp, &s);
    #                           $$ = dlp; }

def p_para_list_2(p):
    '''para_list : para_list T_FLOAT '''
    # { miGeoScalar s = $2;   /* $2 is a double */
    #                           mi_api_dlist_add($1, &s);
    #                           $$ = $1; }




def p_curve_1(p):
    '''curve : CURVE symbol rational symbol _embed0_curve para_list h_vertex_ref_seq curve_spec '''
    # { mi_api_curve_end($6); }

def p__embed0_curve(p):
    '''_embed0_curve : '''
    # { mi_api_curve_begin($2, $4, $3); }

def p_curve_spec_1(p):
    '''curve_spec :  '''

def p_curve_spec_2(p):
    '''curve_spec : SPECIAL curve_special_list '''

def p_curve_special_list_1(p):
    '''curve_special_list : curve_special '''

def p_curve_special_list_2(p):
    '''curve_special_list : curve_special_list curve_special '''

def p_curve_special_1(p):
    '''curve_special : T_INTEGER '''
    # { mi_api_curve_specpnt($1, -1); }

def p_curve_special_2(p):
    '''curve_special : T_INTEGER MAPSTO T_INTEGER '''
    # { mi_api_curve_specpnt($1, $3); }


#    object "object_name"  
#        [ tag label_numberint ]  
#        [ basis list ]  
#        group  
#            vector list  
#            vertex list  
#            [ list of curves ]  
#            space curve  
#            [ list of curve segment references ]  
#        end group  
#    end object  


def p_spacecurve_1(p):
    '''spacecurve : SPACE CURVE symbol _embed0_spacecurve spcurve_list '''
    # { mi_api_spacecurve_end(); }

def p__embed0_spacecurve(p):
    '''_embed0_spacecurve : '''
    # { mi_api_spacecurve_begin($3); }

def p_spcurve_list_1(p):
    '''spcurve_list : symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $2;
    #                           r.max = $3;
    #                           mi_api_spacecurve_curveseg(miTRUE, $1, &r); }

def p_spcurve_list_2(p):
    '''spcurve_list : spcurve_list symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $3;
    #                           r.max = $4;
    #                           mi_api_spacecurve_curveseg(miFALSE, $2, &r); }


#        group  
#            vector list  
#            vertex list  
#            [ list of curves ]  
#            surface  
#            [ list of surface derivative requests ]  
#            [ list of texture or vector surfaces ]  
#            ... # more surfaces  
#            [ list of approximation statements ]  
#            [ list of connection statements ]  
#        end group  

def p_surface_1(p):
    '''surface : SURFACE symbol mtl_or_label _embed0_surface rational symbol floating floating para_list _embed1_surface rational symbol floating floating para_list _embed2_surface h_vertex_ref_seq tex_surf_list surf_spec_list '''
    # { mi_api_surface_end(); }

def p__embed0_surface(p):
    '''_embed0_surface : '''
    # { mi_api_surface_begin($2, $3); }

def p__embed1_surface(p):
    '''_embed1_surface : '''
    # { mi_api_surface_params(miU, $6, $7, $8, $9, $5); }

def p__embed2_surface(p):
    '''_embed2_surface : '''
    # { mi_api_surface_params(miV, $12, $13, $14, $15, $11);}

def p_mtl_or_label_1(p):
    '''mtl_or_label : symbol '''
    # { $$ = $1; }

def p_mtl_or_label_2(p):
    '''mtl_or_label : T_INTEGER '''
    # { $$ = (char *)(miIntptr)$1; }

def p_tex_surf_list_1(p):
    '''tex_surf_list :  '''

def p_tex_surf_list_2(p):
    '''tex_surf_list : tex_surf_list tex_surf '''

def p_tex_surf_1(p):
    '''tex_surf : opt_volume_flag opt_vector_flag TEXTURE rational symbol para_list rational symbol para_list _embed0_tex_surf h_vertex_ref_seq '''

def p_tex_surf_2(p):
    '''tex_surf : DERIVATIVE '''
    # { mi_api_surface_derivative(1); }

def p_tex_surf_3(p):
    '''tex_surf : DERIVATIVE T_INTEGER '''
    # { mi_api_surface_derivative($2); }

def p_tex_surf_4(p):
    '''tex_surf : DERIVATIVE T_INTEGER T_INTEGER '''
    # { mi_api_surface_derivative($2);
    #                           mi_api_surface_derivative($3); }

def p__embed0_tex_surf(p):
    '''_embed0_tex_surf : '''
    # { mi_api_surface_texture_begin(
    #                                         $1, $2, $5, $6, $4, $8, $9, $7); }

def p_opt_volume_flag_1(p):
    '''opt_volume_flag :  '''
    # { $$ = miFALSE; }

def p_opt_volume_flag_2(p):
    '''opt_volume_flag : VOLUME '''
    # { $$ = miTRUE; }

def p_opt_vector_flag_1(p):
    '''opt_vector_flag :  '''
    # { $$ = miFALSE; }

def p_opt_vector_flag_2(p):
    '''opt_vector_flag : VECTOR '''
    # { $$ = miTRUE; }

def p_surf_spec_list_1(p):
    '''surf_spec_list :  '''

def p_surf_spec_list_2(p):
    '''surf_spec_list : surf_spec_list surf_spec '''

def p_surf_spec_1(p):
    '''surf_spec : TRIM trim_spec_list '''

def p_surf_spec_2(p):
    '''surf_spec : HOLE hole_spec_list '''

def p_surf_spec_3(p):
    '''surf_spec : SPECIAL _embed0_surf_spec special_spec_list '''

def p__embed0_surf_spec(p):
    '''_embed0_surf_spec : '''
    # { newloop = miTRUE; }

def p_trim_spec_list_1(p):
    '''trim_spec_list : symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $2;
    #                           r.max = $3;
    #                           mi_api_surface_curveseg(miTRUE, miCURVE_TRIM,$1,&r);}

def p_trim_spec_list_2(p):
    '''trim_spec_list : trim_spec_list symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $3;
    #                           r.max = $4;
    #                           mi_api_surface_curveseg(miFALSE,miCURVE_TRIM,$2,&r);}

def p_hole_spec_list_1(p):
    '''hole_spec_list : symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $2;
    #                           r.max = $3;
    #                           mi_api_surface_curveseg(miTRUE,miCURVE_HOLE,$1,&r); }

def p_hole_spec_list_2(p):
    '''hole_spec_list : hole_spec_list symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $3;
    #                           r.max = $4;
    #                           mi_api_surface_curveseg(miFALSE,miCURVE_HOLE,$2,&r);}

def p_special_spec_list_1(p):
    '''special_spec_list : special_spec '''

def p_special_spec_list_2(p):
    '''special_spec_list : special_spec_list special_spec '''

def p_special_spec_1(p):
    '''special_spec : T_INTEGER '''
    # { mi_api_surface_specpnt($1, -1); }

def p_special_spec_2(p):
    '''special_spec : T_INTEGER MAPSTO T_INTEGER '''
    # { mi_api_surface_specpnt($1, $3); }

def p_special_spec_3(p):
    '''special_spec : symbol floating floating '''
    # { miGeoRange r;
    #                           r.min = $2;
    #                           r.max = $3;
    #                           mi_api_surface_curveseg(newloop,
    #                                                   miCURVE_SPECIAL, $1, &r);
    #                           newloop = miFALSE; }

def p_connection_1(p):
    '''connection : CONNECT symbol symbol floating floating symbol symbol floating floating '''
    # { miGeoRange c1, c2;
    #                           c1.min = $4;
    #                           c1.max = $5;
    #                           c2.min = $8;
    #                           c2.max = $9;
    #                           mi_api_object_group_connection($2,$3,&c1,$6,$7,&c2);}

def p_subdivsurf_1(p):
    '''subdivsurf : SUBDIVISION SURFACE _embed0_subdivsurf sds_surf sds_base_faces derivatives END SUBDIVISION SURFACE '''
    # { mi_api_subdivsurf_end(); }

def p__embed0_subdivsurf(p):
    '''_embed0_subdivsurf : '''
    # { memset(&subdiv_opt, 0, sizeof(subdiv_opt)); }

def p_sds_surf_1(p):
    '''sds_surf : symbol sds_specs '''
    # { mi_api_subdivsurf_begin_x($1, &subdiv_opt); }

def p_sds_specs_1(p):
    '''sds_specs :  '''

def p_sds_specs_2(p):
    '''sds_specs : sds_specs sds_spec '''




def p_sds_spec_1(p):
    '''sds_spec : POLYGON T_INTEGER T_INTEGER T_INTEGER T_INTEGER '''
    # { subdiv_opt.no_basetris  = $2;
    #                           subdiv_opt.no_hiratris  = $3;
    #                           subdiv_opt.no_basequads = $4;
    #                           subdiv_opt.no_hiraquads = $5;
    #                           subdiv_opt.no_vertices  = 0; }

def p_sds_spec_2(p):
    '''sds_spec : TEXTURE SPACE _embed0_sds_spec '[' texspace ']' '''
    # { mi_api_subdivsurf_texspace(subdiv_texspace,
    #                                                      texspace_idx); }

def p__embed0_sds_spec(p):
    '''_embed0_sds_spec : '''
    # { texspace_idx = 0; }

def p_texspace_1(p):
    '''texspace : FACE texspace_nxt '''
    # { subdiv_texspace[texspace_idx++].face = miTRUE; }

def p_texspace_2(p):
    '''texspace : SUBDIVISION texspace_nxt '''
    # { subdiv_texspace[texspace_idx++].face = miFALSE; }

def p_texspace_nxt_1(p):
    '''texspace_nxt :  '''

def p_texspace_nxt_2(p):
    '''texspace_nxt : ',' '''

def p_texspace_nxt_3(p):
    '''texspace_nxt : ',' texspace '''

def p_derivatives_1(p):
    '''derivatives :  '''

def p_derivatives_2(p):
    '''derivatives : derivatives derivative '''

def p_derivative_1(p):
    '''derivative : DERIVATIVE T_INTEGER '''
    # { mi_api_subdivsurf_derivative($2, 0); }

def p_derivative_2(p):
    '''derivative : DERIVATIVE T_INTEGER SPACE T_INTEGER '''
    # { mi_api_subdivsurf_derivative($2, $4); }

def p_sds_base_faces_1(p):
    '''sds_base_faces :  '''

def p_sds_base_faces_2(p):
    '''sds_base_faces : sds_base_faces sds_base_face '''

def p_sds_base_face_1(p):
    '''sds_base_face : P opt_symbol sds_indices _embed0_sds_base_face base_data '''

def p__embed0_sds_base_face(p):
    '''_embed0_sds_base_face : '''
    # { mi_api_subdivsurf_baseface();
    #                           mi_api_subdivsurf_mtl(-1, $2); }

def p_base_data_1(p):
    '''base_data :  '''

def p_base_data_2(p):
    '''base_data : base_spec base_data '''

def p_base_spec_1(p):
    '''base_spec : '{' _embed0_base_spec hira_data '}' '''
    # { mi_api_subdivsurf_pop(); }

def p_base_spec_2(p):
    '''base_spec : CREASE T_INTEGER sds_creaseflags '''
    # { mi_api_subdivsurf_crease(-1, $2); }

def p_base_spec_3(p):
    '''base_spec : TRIM T_INTEGER '''
    # { mi_api_subdivsurf_trim(-1, $2); }

def p__embed0_base_spec(p):
    '''_embed0_base_spec : '''
    # { mi_api_subdivsurf_push();
    #                           mi_api_subdivsurf_subdivide(-1); }

def p_hira_data_1(p):
    '''hira_data :  '''

def p_hira_data_2(p):
    '''hira_data : hira_spec hira_data '''

def p_hira_spec_1(p):
    '''hira_spec : MATERIAL T_INTEGER symbol '''
    # { mi_api_subdivsurf_mtl($2, $3); }

def p_hira_spec_2(p):
    '''hira_spec : MATERIAL T_INTEGER T_INTEGER '''
    # { mi_api_subdivsurf_mtl_tag($2, $3); }

def p_hira_spec_3(p):
    '''hira_spec : DETAIL T_INTEGER sds_indices '''
    # { mi_api_subdivsurf_detail($2); }

def p_hira_spec_4(p):
    '''hira_spec : CREASE T_INTEGER T_INTEGER sds_creaseflags '''
    # { mi_api_subdivsurf_crease($2, $3); }

def p_hira_spec_5(p):
    '''hira_spec : TRIM T_INTEGER T_INTEGER '''
    # { mi_api_subdivsurf_trim($2, $3); }

def p_hira_spec_6(p):
    '''hira_spec : CHILD T_INTEGER '{' _embed0_hira_spec hira_data '}' '''
    # { mi_api_subdivsurf_pop(); }

def p__embed0_hira_spec(p):
    '''_embed0_hira_spec : '''
    # { mi_api_subdivsurf_push();
    #                           mi_api_subdivsurf_subdivide($2); }

def p_sds_indices_1(p):
    '''sds_indices :  '''

def p_sds_indices_2(p):
    '''sds_indices : T_INTEGER _embed0_sds_indices sds_indices '''

def p__embed0_sds_indices(p):
    '''_embed0_sds_indices : '''
    # { mi_api_subdivsurf_index($1); }

def p_sds_creaseflags_1(p):
    '''sds_creaseflags :  '''

def p_sds_creaseflags_2(p):
    '''sds_creaseflags : floating _embed0_sds_creaseflags sds_creaseflags '''

def p__embed0_sds_creaseflags(p):
    '''_embed0_sds_creaseflags : '''
    # { mi_api_subdivsurf_crease_edge($1); }



def p_ccmesh_1(p):
    '''ccmesh : CCMESH symbol POLYGON T_INTEGER VERTEX T_INTEGER _embed0_ccmesh ccmesh_polys ccmesh_derivs END CCMESH '''
    # { mi_api_ccmesh_end(); ccmesh_mtl = 0; }

def p__embed0_ccmesh(p):
    '''_embed0_ccmesh : '''
    # { miApi_ccmesh_options opt;
    #                           opt.no_polygons = $4;
    #                           opt.no_vertices = $6;
    #                           mi_api_ccmesh_begin($2, &opt);
    #                           ccmesh_nvtx    = 0;
    #                           ccmesh_ncrease = 0;
    #                           ccmesh_mtl     = 0;
    #                           ccmesh_needslabel = curr_obj->mtl_is_label; }

def p_ccmesh_polys_1(p):
    '''ccmesh_polys : P symbol ccmesh_vertices _embed0_ccmesh_polys ccmesh_crease ccmesh_sym '''

def p_ccmesh_polys_2(p):
    '''ccmesh_polys : P _embed1_ccmesh_polys ccmesh_vertices _embed2_ccmesh_polys ccmesh_crease ccmesh_nosym '''

def p__embed0_ccmesh_polys(p):
    '''_embed0_ccmesh_polys : '''
    # { ccmesh_mtl = mi_api_material_lookup($2);
    #                           mi_api_ccmesh_polygon(ccmesh_nvtx,
    #                                     ctx->ccmesh_vtx, ccmesh_mtl);
    #                           ccmesh_nvtx = 0; }

def p__embed1_ccmesh_polys(p):
    '''_embed1_ccmesh_polys : '''
    # { ccmesh_label = ccmesh_needslabel; }

def p__embed2_ccmesh_polys(p):
    '''_embed2_ccmesh_polys : '''
    # { 
    #                           mi_api_ccmesh_polygon(ccmesh_nvtx,
    #                                     ctx->ccmesh_vtx, ccmesh_mtl);
    #                           ccmesh_nvtx = 0; }

def p_ccmesh_sym_1(p):
    '''ccmesh_sym :  '''

def p_ccmesh_sym_2(p):
    '''ccmesh_sym : ccmesh_sym P opt_symbol ccmesh_vertices _embed0_ccmesh_sym ccmesh_crease '''

def p__embed0_ccmesh_sym(p):
    '''_embed0_ccmesh_sym : '''
    # { if ($3)
    #                                 ccmesh_mtl = mi_api_material_lookup($3);
    #                           mi_api_ccmesh_polygon(ccmesh_nvtx,
    #                                     ctx->ccmesh_vtx, ccmesh_mtl);
    #                           ccmesh_nvtx = 0; }

def p_ccmesh_nosym_1(p):
    '''ccmesh_nosym :  '''

def p_ccmesh_nosym_2(p):
    '''ccmesh_nosym : ccmesh_nosym P _embed0_ccmesh_nosym ccmesh_vertices _embed1_ccmesh_nosym ccmesh_crease '''

def p__embed0_ccmesh_nosym(p):
    '''_embed0_ccmesh_nosym : '''
    # { ccmesh_label = ccmesh_needslabel; }

def p__embed1_ccmesh_nosym(p):
    '''_embed1_ccmesh_nosym : '''
    # { mi_api_ccmesh_polygon(ccmesh_nvtx,
    #                                     ctx->ccmesh_vtx, ccmesh_mtl);
    #                           ccmesh_nvtx = 0; }

def p_ccmesh_vertices_1(p):
    '''ccmesh_vertices :  '''

def p_ccmesh_vertices_2(p):
    '''ccmesh_vertices : ccmesh_vertices T_INTEGER '''
    # { if (ccmesh_label) {
    #                                 ccmesh_mtl = $2;
    #                                 ccmesh_label = miFALSE;
    #                           } else {
    #                                 if (ccmesh_nvtx+1 > ctx->ccmesh_vtx_size) {
    #                                         ctx->ccmesh_vtx_size =
    #                                                 ctx->ccmesh_vtx_size * 3 / 2;
    #                                         ctx->ccmesh_vtx = (miUint*)
    #                                                         mi_api_reallocate(
    #                                         ctx->ccmesh_vtx,
    #                                         sizeof(miUint) * ctx->ccmesh_vtx_size);
    #                                 }
    #                                 ctx->ccmesh_vtx[ccmesh_nvtx++] = $2; } }

def p_ccmesh_crease_1(p):
    '''ccmesh_crease :  '''

def p_ccmesh_crease_2(p):
    '''ccmesh_crease : CREASE ccmesh_cvalues '''
    # { mi_api_ccmesh_crease(ctx->ccmesh_crease);
    #                           ccmesh_ncrease = 0; }

def p_ccmesh_cvalues_1(p):
    '''ccmesh_cvalues :  '''

def p_ccmesh_cvalues_2(p):
    '''ccmesh_cvalues : ccmesh_cvalues floating '''
    # { if (ccmesh_ncrease+1 > ctx->ccmesh_crease_size) {
    #                                 ctx->ccmesh_crease_size =
    #                                         ctx->ccmesh_crease_size * 3 / 2;
    #                                 ctx->ccmesh_crease = (miScalar*)
    #                                                         mi_api_reallocate(
    #                                     ctx->ccmesh_crease, sizeof(miScalar) *
    #                                     ctx->ccmesh_crease_size);
    #                           }
    #                           ctx->ccmesh_crease[ccmesh_ncrease++] = $2; }

def p_ccmesh_derivs_1(p):
    '''ccmesh_derivs :  '''

def p_ccmesh_derivs_2(p):
    '''ccmesh_derivs : ccmesh_derivs ccmesh_deriv '''

def p_ccmesh_deriv_1(p):
    '''ccmesh_deriv : DERIVATIVE T_INTEGER '''
    # { mi_api_ccmesh_derivative($2, 0); }

def p_ccmesh_deriv_2(p):
    '''ccmesh_deriv : DERIVATIVE T_INTEGER SPACE T_INTEGER '''
    # { mi_api_ccmesh_derivative($2, $4); }


#    object "nameobject"  
#        [ visible [on|off] ]  
#        [ shadow [on|off] ]  
#        [ shadowmap [on|off] ]  
#        [ trace [on|off] ]  
#        [ reflection [mode] ]
#        [ refraction [mode] ]
#        [ transparency [mode] ]
#        [ select [on|off] ]  
#        [ tagged [on|off] ]  
#        [ caustic [on|off] ]  
#        [ globillum [on|off] ]  
#        [ caustic [mode] ]  
#        [ globillum [mode] ]  
#        [ finalgather [mode] ]
#        [ box [xmin ymin zmin xmax ymax zmax] ]  
#        [ motion box [xmin ymin zmin xmax ymax zmax] ]  
#        [ max displace value ]  
#        [ samples min  max ]  
#        [ data null|"namedata" ]  
#        [ tag numberlabelint ]  
#        hair  
#            [ material "namematerial" ]  
#            [ radius radius ]  
#            [ approximate segments ]  
#            [ degree degree ]  
#            [ max size size ]  
#            [ max depth depth ]  
#            [ hair n ]  
#            [ hair m hm ]  
#            [ hair t ht ]  
#            [ hair u hu ]  
#            [ hair radius ]  
#            [ vertex n ]  
#            [ vertex m vm ]  
#            [ vertex t vt ]  
#            [ vertex u vu ]  
#            [ vertex radius ]  
#            scalar [ nscalars ]  
#                scalar list  
#            hair [ nhairs ]  
#                hair offset list  
#        end hair  
#    end object  
    
def p_hair_object_1(p):
    '''hair_object : HAIR _embed0_hair_object hair_options SCALAR '[' T_INTEGER ']' _embed1_hair_object hair_scalars _embed2_hair_object HAIR '[' T_INTEGER ']' _embed3_hair_object hair_hairs _embed4_hair_object END HAIR '''

def p__embed0_hair_object(p):
    '''_embed0_hair_object : '''
    # { hair = mi_api_hair_begin(); }

def p__embed1_hair_object(p):
    '''_embed1_hair_object : '''
    # { hair_index   = 0;
    #                           hair_scalars = mi_api_hair_scalars_begin($6); }

def p__embed2_hair_object(p):
    '''_embed2_hair_object : '''
    # { mi_api_hair_scalars_end(hair_index); }

def p__embed3_hair_object(p):
    '''_embed3_hair_object : '''
    # { hair_indices = mi_api_hair_hairs_begin($13); }

def p__embed4_hair_object(p):
    '''_embed4_hair_object : '''
    # { mi_api_hair_hairs_end();
    #                           mi_api_hair_end(); }

def p_hair_options_1(p):
    '''hair_options : hair_option hair_options '''

def p_hair_options_2(p):
    '''hair_options :  '''

def p_hair_option_1(p):
    '''hair_option : MATERIAL symbol '''
    # { hair->material = mi_api_material_lookup($2); }

def p_hair_option_2(p):
    '''hair_option : RADIUS floating '''
    # { hair->radius = $2; }

def p_hair_option_3(p):
    '''hair_option : APPROXIMATE T_INTEGER '''
    # { hair->approx = $2; }

def p_hair_option_4(p):
    '''hair_option : DEGREE T_INTEGER '''
    # { hair->degree = $2; }

def p_hair_option_5(p):
    '''hair_option : MAX SIZE T_INTEGER '''
    # { hair->space_max_size  = $3; }

def p_hair_option_6(p):
    '''hair_option : MAX DEPTH T_INTEGER '''
    # { hair->space_max_depth = $3; }

def p_hair_option_7(p):
    '''hair_option : HAIR N '''
    # { mi_api_hair_info(0, 'n', 3); }

def p_hair_option_8(p):
    '''hair_option : HAIR M T_INTEGER '''
    # { mi_api_hair_info(0, 'm', 3*$3); }

def p_hair_option_9(p):
    '''hair_option : HAIR T T_INTEGER '''
    # { mi_api_hair_info(0, 't', $3); }

def p_hair_option_10(p):
    '''hair_option : HAIR RADIUS '''
    # { mi_api_hair_info(0, 'r', 1); }

def p_hair_option_11(p):
    '''hair_option : HAIR U T_INTEGER '''
    # { mi_api_hair_info(0, 'u', $3); }

def p_hair_option_12(p):
    '''hair_option : VERTEX N '''
    # { mi_api_hair_info(1, 'n', 3); }

def p_hair_option_13(p):
    '''hair_option : VERTEX M T_INTEGER '''
    # { mi_api_hair_info(1, 'm', 3*$3); }

def p_hair_option_14(p):
    '''hair_option : VERTEX T T_INTEGER '''
    # { mi_api_hair_info(1, 't', $3); }

def p_hair_option_15(p):
    '''hair_option : VERTEX RADIUS '''
    # { mi_api_hair_info(1, 'r', 1); }

def p_hair_option_16(p):
    '''hair_option : VERTEX U T_INTEGER '''
    # { mi_api_hair_info(1, 'u', $3); }

def p_hair_scalars_1(p):
    '''hair_scalars : BINARY _embed0_hair_scalars T_VECTOR '''
    # { hair_index  = hair->no_scalars; }

def p_hair_scalars_2(p):
    '''hair_scalars : hair_scalars_a '''

def p__embed0_hair_scalars(p):
    '''_embed0_hair_scalars : '''
    # { ctx->read_integer = hair->no_scalars;
    #                           ctx->ri_buf = (int*)hair_scalars; }

def p_hair_scalars_a_1(p):
    '''hair_scalars_a :  '''

def p_hair_scalars_a_2(p):
    '''hair_scalars_a : hair_scalars_a floating '''
    # { if (hair_index < hair->no_scalars)
    #                                 hair_scalars[hair_index] = $2;
    #                           hair_index++; }

def p_hair_hairs_1(p):
    '''hair_hairs : BINARY _embed0_hair_hairs T_VECTOR '''

def p_hair_hairs_2(p):
    '''hair_hairs : hair_hairs_a '''

def p__embed0_hair_hairs(p):
    '''_embed0_hair_hairs : '''
    # { ctx->read_integer = hair->no_hairs+1;
    #                           ctx->ri_buf = (int*)hair_indices; }

def p_hair_hairs_a_1(p):
    '''hair_hairs_a :  '''

def p_hair_hairs_a_2(p):
    '''hair_hairs_a : hair_hairs_a T_INTEGER '''
    # { mi_api_hair_hairs_add($2); }





def p_trilist_object_1(p):
    '''trilist_object : TRILIST _embed0_trilist_object VECTOR '[' T_INTEGER ']' VERTEX '[' T_INTEGER ']' P tl_specs TRIANGLE '[' T_INTEGER ']' _embed1_trilist_object '[' tl_vectors ']' '[' tl_vertices ']' '[' tl_triangles ']' END TRILIST _embed2_trilist_object tl_approx '''

def p_trilist_object_2(p):
    '''trilist_object : TRILIST VERTEX T_INTEGER P _embed3_trilist_object pl_specs TRIANGLE T_INTEGER pl_border pl_priminfo _embed4_trilist_object pl_lines pl_prims pl_borderprims pl_primdata pl_topology END TRILIST _embed5_trilist_object tl_approx '''

def p__embed0_trilist_object(p):
    '''_embed0_trilist_object : '''
    # { memset(&tlcont, 0, sizeof(tlcont));
    #                           tlcont.sizeof_vertex++; }

def p__embed1_trilist_object(p):
    '''_embed1_trilist_object : '''
    # { tlbox = mi_api_trilist_begin(&tlcont,
    #                                         $5, $9, $15);
    #                           tlvec     = tlbox->vectors;
    #                           tlvert    = miBOX_GET_VERTICES(tlbox);
    #                           tlvec_idx = tlvert_idx = tl_ind = 0;
    #                           tl_nvec   = $5;
    #                           tl_nvert  = $9 * tlcont.sizeof_vertex;
    #                           tl_nind   = tlbox->mtl_is_label ? 4 : 3; }

def p__embed2_trilist_object(p):
    '''_embed2_trilist_object : '''
    # { mi_api_trilist_end(); }

def p__embed3_trilist_object(p):
    '''_embed3_trilist_object : '''
    # { memset(&plinfo, 0, sizeof(plinfo));
    #                           plinfo.line_size = 3;
    #                           pl_priminfosize = 0;
    #                           pl_primdatasize = 0; }

def p__embed4_trilist_object(p):
    '''_embed4_trilist_object : '''
    # { miUint no_prims = $8 + $9;
    #                           miUint no_plist = $9 ? 2 : 1;
    #                           plbox = mi_api_primlist_begin_2(&plinfo,
    #                                         $3, no_plist, no_prims * 3,
    #                                         no_prims,       /* no_materials */
    #                                         pl_primdatasize,/* primdata_size */
    #                                         pl_priminfosize,/* pd_info_size */
    #                                         no_prims);
    #                           if ($9)
    #                                 mi_api_primlist_border(1, $9);
    #                           pllines = miBOX_VERTEX_LINES(plbox);
    #                           plprims = miBOX_PRIMS(plbox);
    #                           plmtls  = miBOX_MATERIALS(plbox);
    #                           pl_priminfo = miBOX_PD_INFO(plbox);
    #                           pl_primdata = miBOX_PRIMDATA(plbox);
    #                           *plprims++ = miSCENE_PRIMLIST_MAKE_CODE(
    #                                         miSCENE_PRIM_TRI, $8 * 3);
    #                           mi_api_primlist_dimensions(pl_texo, pl_uso);
    #                           tl_nind = plbox->mtl_is_label ? 4 : 3;
    #                           tl_ind = 0; pl_no_prims = $8; }

def p__embed5_trilist_object(p):
    '''_embed5_trilist_object : '''
    # { miUint no_prims = $8 + $9;
    #                           miUint no_plist = $9 ? 2 : 1;
    #                           mi_api_primlist_end();
    #                           if (plprims != miBOX_PRIMS(plbox)+
    #                               no_prims*3+no_plist)
    #                                 mi_api_error("wrong number of triangles");
    #                           if (pllines != miBOX_VERTEX_LINES(plbox) + $3 *
    #                               plinfo.line_size)
    #                                 mi_api_error("wrong number of scalars");
    #                           if (pl_priminfo !=
    #                               miBOX_PD_INFO(plbox) + pl_priminfosize)
    #                                 mi_api_error("wrong prim info size");
    #                           if (pl_primdata !=
    #                               miBOX_PRIMDATA(plbox) +
    #                               pl_primdatasize * no_prims)
    #                                 mi_api_error("wrong prim data size"); }

def p_pl_topology_1(p):
    '''pl_topology :  '''

def p_pl_topology_2(p):
    '''pl_topology : TOPOLOGY _embed0_pl_topology pl_top '''
    # { mi_api_primlist_topology(pltop);
    #                           mi_api_release(pltop); }

def p__embed0_pl_topology(p):
    '''_embed0_pl_topology : '''
    # { pltop = (miUint*) mi_api_allocate(sizeof(miUint) *
    #                                                 plbox->no_prims*3);
    #                           cur_pltop = pltop; }

def p_pl_top_1(p):
    '''pl_top : '[' pl_top_ascii ']' '''

def p_pl_top_2(p):
    '''pl_top : INTEGER _embed0_pl_top T_VECTOR '''

def p__embed0_pl_top(p):
    '''_embed0_pl_top : '''
    # { ctx->read_integer = plbox->no_prims*3;
    #                           ctx->ri_buf = (int*)pltop; }

def p_pl_top_ascii_1(p):
    '''pl_top_ascii :  '''

def p_pl_top_ascii_2(p):
    '''pl_top_ascii : pl_top_ascii T_INTEGER '''
    # { *cur_pltop++ = $2; }

def p_pl_border_1(p):
    '''pl_border :  '''
    # { $$ = 0; }

def p_pl_border_2(p):
    '''pl_border : BORDER T_INTEGER '''
    # { $$ = $2; }

def p_pl_priminfo_1(p):
    '''pl_priminfo :  '''

def p_pl_priminfo_2(p):
    '''pl_priminfo : DATA T_INTEGER T_INTEGER '''
    # { pl_priminfosize = $2; pl_primdatasize = $3; }

def p_pl_primdata_1(p):
    '''pl_primdata :  '''

def p_pl_primdata_2(p):
    '''pl_primdata : TRIANGLE DATA '[' pl_priminfodata_a ']' '[' pl_primdata_a ']' '''

def p_pl_primdata_3(p):
    '''pl_primdata : TRIANGLE DATA INTEGER _embed0_pl_primdata T_VECTOR INTEGER _embed1_pl_primdata T_VECTOR '''
    # { pl_priminfo += pl_priminfosize;
    #                           pl_primdata += pl_primdatasize * plbox->no_prims; }

def p__embed0_pl_primdata(p):
    '''_embed0_pl_primdata : '''
    # { ctx->read_integer = pl_priminfosize;
    #                           ctx->ri_buf = (int*)pl_priminfo; }

def p__embed1_pl_primdata(p):
    '''_embed1_pl_primdata : '''
    # { ctx->read_integer =
    #                                 pl_primdatasize * plbox->no_prims;
    #                           ctx->ri_buf = (int*)pl_primdata; }

def p_pl_priminfodata_a_1(p):
    '''pl_priminfodata_a :  '''

def p_pl_priminfodata_a_2(p):
    '''pl_priminfodata_a : pl_priminfodata_a T_INTEGER '''
    # { *pl_priminfo++ = $2; }

def p_pl_primdata_a_1(p):
    '''pl_primdata_a :  '''

def p_pl_primdata_a_2(p):
    '''pl_primdata_a : pl_primdata_a T_INTEGER '''
    # { *pl_primdata++ = $2; }

def p_pl_lines_1(p):
    '''pl_lines : SCALAR _embed0_pl_lines T_VECTOR '''
    # { pllines += plinfo.line_size *
    #                                         miBOX_NO_VTXLINES(plbox); }

def p_pl_lines_2(p):
    '''pl_lines : '[' pl_ascii_lines ']' '''

def p__embed0_pl_lines(p):
    '''_embed0_pl_lines : '''
    # { ctx->read_integer = plinfo.line_size *
    #                                         miBOX_NO_VTXLINES(plbox);
    #                           ctx->ri_buf = (int*)pllines; }

def p_pl_ascii_lines_1(p):
    '''pl_ascii_lines :  '''

def p_pl_ascii_lines_2(p):
    '''pl_ascii_lines : pl_ascii_lines floating '''
    # { *pllines++ = $2; }

def p_pl_borderprims_1(p):
    '''pl_borderprims :  '''

def p_pl_borderprims_2(p):
    '''pl_borderprims : _embed0_pl_borderprims pl_prims '''

def p__embed0_pl_borderprims(p):
    '''_embed0_pl_borderprims : '''
    # { *plprims++ = miSCENE_PRIMLIST_MAKE_CODE(
    #                                         miSCENE_PRIM_TRI,
    #                                         plbox->no_border_prims * 3);
    #                     pl_no_prims = plbox->no_border_prims;
    #                   }

def p_pl_prims_1(p):
    '''pl_prims : '[' symbol T_INTEGER T_INTEGER T_INTEGER _embed0_pl_prims pl_tri_mtl ']' '''

def p_pl_prims_2(p):
    '''pl_prims : pl_tri_index '''

def p__embed0_pl_prims(p):
    '''_embed0_pl_prims : '''
    # { *plmtls++ = mi_api_material_lookup($2);
    #                           *plprims++ = $3; *plprims++ = $4;
    #                           *plprims++ = $5; }

def p_pl_tri_mtl_1(p):
    '''pl_tri_mtl :  '''

def p_pl_tri_mtl_2(p):
    '''pl_tri_mtl : pl_tri_mtl opt_symbol T_INTEGER T_INTEGER T_INTEGER '''
    # { *plmtls++ = ($2) ? mi_api_material_lookup($2)
    #                                            : *(plmtls-2);
    #                           *plprims++ = $3; *plprims++ = $4;
    #                           *plprims++ = $5; }

def p_pl_tri_index_1(p):
    '''pl_tri_index : INTEGER _embed0_pl_tri_index T_VECTOR _embed1_pl_tri_index INTEGER _embed2_pl_tri_index T_VECTOR '''
    # { plmtls += pl_no_prims; }

def p_pl_tri_index_2(p):
    '''pl_tri_index : '[' pl_tri_ascindex ']' '''

def p__embed0_pl_tri_index(p):
    '''_embed0_pl_tri_index : '''
    # { if (tl_nind != 4)
    #                                 mi_api_error("binary triangles/no "
    #                                                 "tagged mode");
    #                           ctx->read_integer = pl_no_prims*3;
    #                           ctx->ri_buf = (int*)plprims; }

def p__embed1_pl_tri_index(p):
    '''_embed1_pl_tri_index : '''
    # { plprims += pl_no_prims*3; }

def p__embed2_pl_tri_index(p):
    '''_embed2_pl_tri_index : '''
    # { ctx->read_integer = pl_no_prims;
    #                           ctx->ri_buf = (int*)plmtls; }

def p_pl_tri_ascindex_1(p):
    '''pl_tri_ascindex :  '''

def p_pl_tri_ascindex_2(p):
    '''pl_tri_ascindex : pl_tri_ascindex T_INTEGER '''
    # { if (tl_nind == 4 && !(tl_ind++ & 3))
    #                                 *plmtls++ = $2;
    #                           else
    #                                 *plprims++ = $2; }

def p_pl_specs_1(p):
    '''pl_specs :  '''

def p_pl_specs_2(p):
    '''pl_specs : pl_spec pl_specs '''

def p_tex_dims_1(p):
    '''tex_dims :  '''

def p_tex_dims_2(p):
    '''tex_dims : tex_dims T_INTEGER '''
    # { plinfo.line_size += $2;
    #                           pl_texo[plinfo.no_textures] = $2;
    #                           plinfo.no_textures++; }

def p_us_dims_1(p):
    '''us_dims :  '''

def p_us_dims_2(p):
    '''us_dims : us_dims T_INTEGER '''
    # { plinfo.line_size += $2;
    #                           pl_uso[plinfo.no_users] = $2;
    #                           plinfo.no_users++; }

def p_pl_spec_1(p):
    '''pl_spec : N '''
    # { plinfo.normal_offset = plinfo.line_size;
    #                           plinfo.line_size += 3; }

def p_pl_spec_2(p):
    '''pl_spec : D '''
    # { plinfo.derivs_offset = plinfo.line_size;
    #                           plinfo.line_size += 6; }

def p_pl_spec_3(p):
    '''pl_spec : D2 '''
    # { plinfo.derivs2_offset = plinfo.line_size;
    #                           plinfo.line_size += 9; }

def p_pl_spec_4(p):
    '''pl_spec : M opt_size '''
    # { plinfo.motion_offset = plinfo.line_size;
    #                           plinfo.no_motions = $2;
    #                           plinfo.line_size += $2 * 3; }

def p_pl_spec_5(p):
    '''pl_spec : B opt_size '''
    # { plinfo.bump_offset = plinfo.line_size;
    #                           plinfo.no_bumps = $2;
    #                           plinfo.line_size += $2 * 3; }

def p_pl_spec_6(p):
    '''pl_spec : T _embed0_pl_spec tex_dims '''

def p_pl_spec_7(p):
    '''pl_spec : U _embed1_pl_spec us_dims '''

def p__embed0_pl_spec(p):
    '''_embed0_pl_spec : '''
    # { plinfo.texture_offset = plinfo.line_size; }

def p__embed1_pl_spec(p):
    '''_embed1_pl_spec : '''
    # { plinfo.user_offset = plinfo.line_size; }

def p_tl_vectors_1(p):
    '''tl_vectors :  '''

def p_tl_vectors_2(p):
    '''tl_vectors : tl_vectors vector '''
    # { if (tlvec_idx < tl_nvec)
    #                                 tlvec[tlvec_idx++] = $2; }

def p_tl_vertices_1(p):
    '''tl_vertices :  '''

def p_tl_vertices_2(p):
    '''tl_vertices : tl_vertices T_INTEGER '''
    # { if (tlvert_idx < tl_nvert)
    #                                 tlvert[tlvert_idx++] = $2; }

def p_tl_triangles_1(p):
    '''tl_triangles : symbol T_INTEGER T_INTEGER T_INTEGER _embed0_tl_triangles tl_tri_mtl '''

def p_tl_triangles_2(p):
    '''tl_triangles : tl_tri_index '''

def p__embed0_tl_triangles(p):
    '''_embed0_tl_triangles : '''
    # { tl_indbuf[0] = $2; tl_indbuf[1] = $3;
    #                           tl_indbuf[2] = $4;
    #                           mi_api_trilist_triangle($1, tl_indbuf); }

def p_tl_tri_mtl_1(p):
    '''tl_tri_mtl :  '''

def p_tl_tri_mtl_2(p):
    '''tl_tri_mtl : tl_tri_mtl opt_symbol T_INTEGER T_INTEGER T_INTEGER '''
    # { tl_indbuf[0] = $3; tl_indbuf[1] = $4;
    #                           tl_indbuf[2] = $5;
    #                                 mi_api_trilist_triangle($2, tl_indbuf); }

def p_tl_tri_index_1(p):
    '''tl_tri_index :  '''

def p_tl_tri_index_2(p):
    '''tl_tri_index : tl_tri_index T_INTEGER '''
    # { tl_indbuf[tl_ind++] = $2;
    #                           if (tl_ind == tl_nind) {
    #                                 mi_api_trilist_triangles(tl_indbuf, 1);
    #                                 tl_ind = 0;
    #                           }}

def p_tl_specs_1(p):
    '''tl_specs :  '''

def p_tl_specs_2(p):
    '''tl_specs : tl_spec tl_specs '''

def p_tl_spec_1(p):
    '''tl_spec : N '''
    # { tlcont.normal_offset = tlcont.sizeof_vertex;
    #                           tlcont.sizeof_vertex++; }

def p_tl_spec_2(p):
    '''tl_spec : D '''
    # { tlcont.derivs_offset = tlcont.sizeof_vertex;
    #                           tlcont.sizeof_vertex++; }

def p_tl_spec_3(p):
    '''tl_spec : D2 '''
    # { tlcont.derivs2_offset = tlcont.sizeof_vertex;
    #                           tlcont.sizeof_vertex++; }

def p_tl_spec_4(p):
    '''tl_spec : M opt_size '''
    # { tlcont.motion_offset = tlcont.sizeof_vertex;
    #                           tlcont.no_motions = $2;
    #                           tlcont.sizeof_vertex += $2; }

def p_tl_spec_5(p):
    '''tl_spec : T opt_size '''
    # { tlcont.texture_offset = tlcont.sizeof_vertex;
    #                           tlcont.no_textures = $2;
    #                           tlcont.sizeof_vertex += $2; }

def p_tl_spec_6(p):
    '''tl_spec : B opt_size '''
    # { tlcont.bump_offset = tlcont.sizeof_vertex;
    #                           tlcont.no_bumps = $2;
    #                           tlcont.sizeof_vertex += $2; }

def p_tl_spec_7(p):
    '''tl_spec : U opt_size '''
    # { tlcont.user_offset = tlcont.sizeof_vertex;
    #                           tlcont.no_users = $2;
    #                           tlcont.sizeof_vertex += $2; }

def p_opt_size_1(p):
    '''opt_size :  '''
    # { $$ = 1; }

def p_opt_size_2(p):
    '''opt_size : T_INTEGER '''
    # { $$ = $1; }

def p_tl_approx_1(p):
    '''tl_approx :  '''

def p_tl_approx_2(p):
    '''tl_approx : approximation '''

def p_isect_object_1(p):
    '''isect_object : INTERSECTION function '''
    # { curr_obj->type = miOBJECT_INTERSECT_FUNC;
    #                           curr_obj->geo.intersect_func = $2; }

#======================================
# miApproximation : approximation
#======================================
#
#    flags approximate  
#        technique [ minint maxint ]  
#     
#    flags approximate surface  
#        technique [ minint maxint ] [ max maxint ] "surface_name" ...  
#     
#    flags approximate displace  
#        technique [ minint maxint ] "surface_name" ...  
#     
#    flags approximate trim  
#        technique [ minint maxint ] "surface_name" ...  
#     
#    flags approximate curve  
#        technique [ minint maxint ] "curve_name" ...  
#     
#    flags approximate space curve  
#        technique [ minint maxint ] "spacecurve_name" ...  

def p_approximation_1(p):
    '''approximation : _embed0_approximation approx_flags approx_body '''

def p__embed0_approximation(p):
    '''_embed0_approximation : '''
    # { miAPPROX_DEFAULT(approx); }

def p_approx_flags_1(p):
    '''approx_flags :  '''

def p_approx_flags_2(p):
    '''approx_flags : approx_flag approx_flags '''

def p_approx_flag_1(p):
    '''approx_flag : VISIBLE '''
    # { approx.flag |= miAPPROX_FLAG_VISIBLE; }

def p_approx_flag_2(p):
    '''approx_flag : TRACE '''
    # { approx.flag |= miAPPROX_FLAG_TRACE; }

def p_approx_flag_3(p):
    '''approx_flag : SHADOW '''
    # { approx.flag |= miAPPROX_FLAG_SHADOW; }

def p_approx_flag_4(p):
    '''approx_flag : CAUSTIC '''
    # { approx.flag |= miAPPROX_FLAG_CAUSTIC; }

def p_approx_flag_5(p):
    '''approx_flag : GLOBILLUM '''
    # { approx.flag |= miAPPROX_FLAG_GLOBILLUM; }

def p_approx_body_1(p):
    '''approx_body : APPROXIMATE SURFACE s_approx_tech s_approx_names '''

def p_approx_body_2(p):
    '''approx_body : APPROXIMATE SUBDIVISION SURFACE c_approx_tech sds_approx_names '''

def p_approx_body_3(p):
    '''approx_body : APPROXIMATE CCMESH c_approx_tech ccm_approx_names '''

def p_approx_body_4(p):
    '''approx_body : APPROXIMATE DISPLACE s_approx_tech d_approx_names '''

def p_approx_body_5(p):
    '''approx_body : APPROXIMATE CURVE c_approx_tech c_approx_names '''

def p_approx_body_6(p):
    '''approx_body : APPROXIMATE SPACE CURVE c_approx_tech spc_approx_names '''

def p_approx_body_7(p):
    '''approx_body : APPROXIMATE TRIM c_approx_tech t_approx_names '''

def p_approx_body_8(p):
    '''approx_body : APPROXIMATE s_approx_tech '''
    # { mi_api_poly_approx(&approx); }

def p_approx_body_9(p):
    '''approx_body : APPROXIMATE TRILIST s_approx_tech '''
    # { mi_api_trilist_approx(&approx); }

#--------------------------------------
# approximation technique
#--------------------------------------
#
#    view  
#    offscreen  
#    tree  
#    grid  
#    fine3.1  
#    delaunay  
#    [ regular ] parametric u_subdiv [ v_subdiv ]  
#    [ regular ] parametric u_subdiv% [ v_subdiv% ]  
#    any  
#    sharp sharp3.1  
#    length edge  
#    distance dist  
#    angle angle  
#    spatial [ view ] edge  
#    curvature [ view ] dist angle  
#    grading angle  

def p_s_approx_tech_1(p):
    '''s_approx_tech : s_approx_params '''
    # { approx.subdiv[miMIN]  = 0;
    #                           approx.subdiv[miMAX]  = 5;
    #                           approx.max            = miHUGE_INT;
    #                           if (approx.style == miAPPROX_STYLE_FINE ||
    #                               approx.style == miAPPROX_STYLE_FINE_NO_SMOOTHING)
    #                                 approx.subdiv[miMAX] = 7; }

def p_s_approx_tech_2(p):
    '''s_approx_tech : s_approx_params T_INTEGER T_INTEGER '''
    # { approx.subdiv[miMIN]  = $2;
    #                           approx.subdiv[miMAX]  = $3;
    #                           approx.max            = miHUGE_INT; }

def p_s_approx_tech_3(p):
    '''s_approx_tech : s_approx_params MAX T_INTEGER '''
    # { approx.subdiv[miMIN]  = 0;
    #                           approx.subdiv[miMAX]  = 5;
    #                           approx.max            = $3;
    #                           if (approx.style == miAPPROX_STYLE_FINE ||
    #                               approx.style == miAPPROX_STYLE_FINE_NO_SMOOTHING)
    #                                 approx.subdiv[miMAX] = 7; }

def p_s_approx_tech_4(p):
    '''s_approx_tech : s_approx_params T_INTEGER T_INTEGER MAX T_INTEGER '''
    # { approx.subdiv[miMIN]  = $2;
    #                           approx.subdiv[miMAX]  = $3;
    #                           approx.max            = $5; }

def p_s_approx_tech_5(p):
    '''s_approx_tech : s_approx_params SAMPLES T_INTEGER '''
    # { approx.subdiv[miMIN]  = 0;
    #                           approx.subdiv[miMAX]  = 5;
    #                           approx.max            = $3;
    #                           if (approx.style == miAPPROX_STYLE_FINE ||
    #                               approx.style == miAPPROX_STYLE_FINE_NO_SMOOTHING)
    #                                 approx.subdiv[miMAX] = 7; }

def p_s_approx_tech_6(p):
    '''s_approx_tech : s_approx_params T_INTEGER T_INTEGER SAMPLES T_INTEGER '''
    # { approx.subdiv[miMIN]  = $2;
    #                           approx.subdiv[miMAX]  = $3;
    #                           approx.max            = $5; }

def p_c_approx_tech_1(p):
    '''c_approx_tech : c_approx_params '''
    # { approx.subdiv[miMIN]  = 0;
    #                           approx.subdiv[miMAX]  = 5; }

def p_c_approx_tech_2(p):
    '''c_approx_tech : c_approx_params T_INTEGER T_INTEGER '''
    # { approx.subdiv[miMIN]  = $2;
    #                           approx.subdiv[miMAX]  = $3; }

def p_s_approx_params_1(p):
    '''s_approx_params : s_approx_param '''

def p_s_approx_params_2(p):
    '''s_approx_params : s_approx_param s_approx_params '''

def p_c_approx_params_1(p):
    '''c_approx_params : c_approx_param '''

def p_c_approx_params_2(p):
    '''c_approx_params : c_approx_param c_approx_params '''

def p_s_approx_param_1(p):
    '''s_approx_param : x_approx_param '''

def p_s_approx_param_2(p):
    '''s_approx_param : PARAMETRIC floating floating '''
    # { approx.method                 = miAPPROX_PARAMETRIC;
    #                           approx.cnst[miCNST_UPARAM]    = $2;
    #                           approx.cnst[miCNST_VPARAM]    = $3; }

def p_s_approx_param_3(p):
    '''s_approx_param : REGULAR PARAMETRIC floating floating '''
    # { approx.method                 = miAPPROX_REGULAR;
    #                           approx.cnst[miCNST_UPARAM]    = $3;
    #                           approx.cnst[miCNST_VPARAM]    = $4; }

def p_s_approx_param_4(p):
    '''s_approx_param : REGULAR PARAMETRIC floating '%' floating '%' '''
    # { approx.method             = miAPPROX_REGULAR_PERCENT;
    #                           approx.cnst[miCNST_UPARAM]    = $3;
    #                           approx.cnst[miCNST_VPARAM]    = $5; }

def p_s_approx_param_5(p):
    '''s_approx_param : IMPLICIT '''
    # { approx.method                 = miAPPROX_ALGEBRAIC; }

def p_c_approx_param_1(p):
    '''c_approx_param : x_approx_param '''

def p_c_approx_param_2(p):
    '''c_approx_param : PARAMETRIC floating '''
    # { approx.method                 = miAPPROX_PARAMETRIC;
    #                           approx.cnst[miCNST_UPARAM]    = $2;
    #                           approx.cnst[miCNST_VPARAM]    = 1.0; }

def p_c_approx_param_3(p):
    '''c_approx_param : REGULAR PARAMETRIC floating '''
    # { approx.method                 = miAPPROX_REGULAR;
    #                           approx.cnst[miCNST_UPARAM]    = $3;
    #                           approx.cnst[miCNST_VPARAM]    = 1.0; }

def p_c_approx_param_4(p):
    '''c_approx_param : REGULAR PARAMETRIC floating '%' '''
    # { approx.method            = miAPPROX_REGULAR_PERCENT;
    #                           approx.cnst[miCNST_UPARAM]    = $3;
    #                           approx.cnst[miCNST_VPARAM]    = 100.0; }

def p_x_approx_param_1(p):
    '''x_approx_param : VIEW '''
    # { approx.view_dep      |= 1; }

def p_x_approx_param_2(p):
    '''x_approx_param : OFFSCREEN '''
    # { approx.view_dep      |= 2; }

def p_x_approx_param_3(p):
    '''x_approx_param : ANY '''
    # { approx.any            = miTRUE; }

def p_x_approx_param_4(p):
    '''x_approx_param : TREE '''
    # { approx.style          = miAPPROX_STYLE_TREE; }

def p_x_approx_param_5(p):
    '''x_approx_param : GRID '''
    # { approx.style          = miAPPROX_STYLE_GRID; }

def p_x_approx_param_6(p):
    '''x_approx_param : DELAUNAY '''
    # { approx.style          = miAPPROX_STYLE_DELAUNAY; }

def p_x_approx_param_7(p):
    '''x_approx_param : FINE '''
    # { approx.style          = miAPPROX_STYLE_FINE; }

def p_x_approx_param_8(p):
    '''x_approx_param : FINE NOSMOOTHING '''
    # { approx.style = miAPPROX_STYLE_FINE_NO_SMOOTHING; }

def p_x_approx_param_9(p):
    '''x_approx_param : SHARP floating '''
    # { approx.sharp          = $2<0 ? 0   : 
    #                                                   $2>1 ? 255 : 
    #                                                        (miUint1)($2*255.);}

def p_x_approx_param_10(p):
    '''x_approx_param : LENGTH floating '''
    # { approx.method         = miAPPROX_LDA;
    #                           approx.cnst[miCNST_LENGTH]    = $2; }

def p_x_approx_param_11(p):
    '''x_approx_param : DISTANCE floating '''
    # { approx.method                 = miAPPROX_LDA;
    #                           approx.cnst[miCNST_DISTANCE]  = $2; }

def p_x_approx_param_12(p):
    '''x_approx_param : ANGLE floating '''
    # { approx.method                 = miAPPROX_LDA;
    #                           approx.cnst[miCNST_ANGLE]     = $2; }

def p_x_approx_param_13(p):
    '''x_approx_param : SPATIAL approx_view floating '''
    # { approx.method                 = miAPPROX_SPATIAL;
    #                           approx.cnst[miCNST_LENGTH]    = $3; }

def p_x_approx_param_14(p):
    '''x_approx_param : CURVATURE approx_view floating floating '''
    # { approx.method                 = miAPPROX_CURVATURE;
    #                           approx.cnst[miCNST_DISTANCE]  = $3;
    #                           approx.cnst[miCNST_ANGLE]     = $4; }

def p_x_approx_param_15(p):
    '''x_approx_param : GRADING floating '''
    # { approx.grading                = $2; }

def p_approx_view_1(p):
    '''approx_view :  '''

def p_approx_view_2(p):
    '''approx_view : VIEW '''
    # { approx.view_dep              |= 1; }

def p_approx_view_3(p):
    '''approx_view : OFFSCREEN '''
    # { approx.view_dep              |= 2; }

def p_s_approx_names_1(p):
    '''s_approx_names : symbol '''
    # { mi_api_surface_approx($1, &approx); }

def p_s_approx_names_2(p):
    '''s_approx_names : s_approx_names symbol '''
    # { mi_api_surface_approx($2, &approx); }

def p_sds_approx_names_1(p):
    '''sds_approx_names : symbol '''
    # { mi_api_subdivsurf_approx($1, &approx); }

def p_sds_approx_names_2(p):
    '''sds_approx_names : sds_approx_names symbol '''
    # { mi_api_subdivsurf_approx($2, &approx); }

def p_ccm_approx_names_1(p):
    '''ccm_approx_names : symbol '''
    # { mi_api_ccmesh_approx($1, &approx); }

def p_ccm_approx_names_2(p):
    '''ccm_approx_names : ccm_approx_names symbol '''
    # { mi_api_ccmesh_approx($2, &approx); }

def p_d_approx_names_1(p):
    '''d_approx_names : symbol '''
    # { mi_api_surface_approx_displace($1, &approx); }

def p_d_approx_names_2(p):
    '''d_approx_names : s_approx_names symbol '''
    # { mi_api_surface_approx_displace($2, &approx); }

def p_c_approx_names_1(p):
    '''c_approx_names : symbol '''
    # { mi_api_curve_approx($1, &approx); }

def p_c_approx_names_2(p):
    '''c_approx_names : c_approx_names symbol '''
    # { mi_api_curve_approx($2, &approx); }

def p_spc_approx_names_1(p):
    '''spc_approx_names : symbol '''
    # { mi_api_spacecurve_approx($1, &approx); }

def p_spc_approx_names_2(p):
    '''spc_approx_names : c_approx_names symbol '''
    # { mi_api_spacecurve_approx($2, &approx); }

def p_t_approx_names_1(p):
    '''t_approx_names : symbol '''
    # { mi_api_surface_approx_trim($1, &approx); }

def p_t_approx_names_2(p):
    '''t_approx_names : t_approx_names symbol '''
    # { mi_api_surface_approx_trim($2, &approx); }




def p_options_attribute_1(p):
    '''options_attribute : ATTRIBUTE opt_override options_attribute_item '''

def p_options_attribute_2(p):
    '''options_attribute : ATTRIBUTE opt_override attr_flag '''

def p_options_attribute_3(p):
    '''options_attribute : AMBIENTOCCLUSION boolean '''

def p_options_attribute_4(p):
    '''options_attribute : AMBIENTOCCLUSION REBUILD boolean '''

def p_options_attribute_5(p):
    '''options_attribute : AMBIENTOCCLUSION REBUILD FREEZE '''

def p_options_attribute_6(p):
    '''options_attribute : AMBIENTOCCLUSION FILTER filter_type '''

def p_options_attribute_7(p):
    '''options_attribute : AMBIENTOCCLUSION FILTER filter_type floating '''

def p_options_attribute_8(p):
    '''options_attribute : AMBIENTOCCLUSION IMPORTANCE floating '''

def p_options_attribute_9(p):
    '''options_attribute : AMBIENTOCCLUSION IMPORTANCE floating floating '''

def p_options_attribute_10(p):
    '''options_attribute : AMBIENTOCCLUSION FALLOFF floating '''

def p_options_attribute_11(p):
    '''options_attribute : AMBIENTOCCLUSION FALLOFF floating floating '''

def p_options_attribute_12(p):
    '''options_attribute : AMBIENTOCCLUSION ACCURACY floating '''

def p_options_attribute_13(p):
    '''options_attribute : AMBIENTOCCLUSION ACCURACY floating floating '''

def p_options_attribute_14(p):
    '''options_attribute : IBL boolean '''

def p_options_attribute_15(p):
    '''options_attribute : IBL FALLOFF floating '''

def p_options_attribute_16(p):
    '''options_attribute : IBL FALLOFF floating floating '''

def p_options_attribute_17(p):
    '''options_attribute : IBL ACCURACY floating '''

def p_options_attribute_18(p):
    '''options_attribute : IBL ACCURACY floating floating '''

def p_options_attribute_19(p):
    '''options_attribute : IBL JITTER boolean '''

def p_options_attribute_20(p):
    '''options_attribute : FINALGATHER IMPORTANCE floating '''

def p_options_attribute_21(p):
    '''options_attribute : FINALGATHER IMPORTANCE floating floating '''

def p_options_attribute_22(p):
    '''options_attribute : TRACE IMPORTANCE floating '''

def p_options_attribute_23(p):
    '''options_attribute : TRACE IMPORTANCE floating floating '''

def p_options_attribute_24(p):
    '''options_attribute : TRACE FALLOFF floating '''

def p_options_attribute_25(p):
    '''options_attribute : TRACE FALLOFF floating floating '''

def p_options_attribute_26(p):
    '''options_attribute : GLOBILLUM IMPORTANCE floating '''

def p_options_attribute_27(p):
    '''options_attribute : GLOBILLUM IMPORTANCE floating floating '''

def p_options_attribute_28(p):
    '''options_attribute : GLOBILLUM FALLOFF floating '''

def p_options_attribute_29(p):
    '''options_attribute : GLOBILLUM FALLOFF floating floating '''

def p_options_attribute_30(p):
    '''options_attribute : CAUSTIC IMPORTANCE floating '''

def p_options_attribute_31(p):
    '''options_attribute : CAUSTIC IMPORTANCE floating floating '''

def p_options_attribute_32(p):
    '''options_attribute : CAUSTIC FALLOFF floating '''

def p_options_attribute_33(p):
    '''options_attribute : CAUSTIC FALLOFF floating floating '''

def p_options_attribute_item_1(p):
    '''options_attribute_item : decl_modifiers BOOLEAN T_STRING boolean '''
    # { string_options->set($3, $4 != 0); 
    #                           mi_api_release($3); }

def p_options_attribute_item_2(p):
    '''options_attribute_item : decl_modifiers INTEGER T_STRING T_INTEGER '''
    # { string_options->set($3, $4);
    #                           mi_api_release($3); }

def p_options_attribute_item_3(p):
    '''options_attribute_item : decl_modifiers SCALAR T_STRING floating '''
    # { string_options->set($3, (float)$4);
    #                           mi_api_release($3); }

def p_options_attribute_item_4(p):
    '''options_attribute_item : decl_modifiers COLOR T_STRING floating floating floating floating '''
    # { string_options->set($3, (float)$4, (float)$5, (float)$6, (float)$7);
    #                           mi_api_release($3); }

def p_options_attribute_item_5(p):
    '''options_attribute_item : decl_modifiers VECTOR T_STRING floating floating floating '''
    # { string_options->set($3, (float)$4, (float)$5, (float)$6);
    #                           mi_api_release($3); }

def p_options_attribute_item_6(p):
    '''options_attribute_item : decl_modifiers STRING T_STRING T_STRING '''
    # { string_options->set($3, $4);
    #                           mi_api_release($3);
    #                           mi_api_release($4); }

def p_dummy_attribute_1(p):
    '''dummy_attribute : ATTRIBUTE opt_override dummy_attribute_item '''

def p_dummy_attribute_2(p):
    '''dummy_attribute : ATTRIBUTE opt_override attr_flag '''

def p_dummy_attribute_item_1(p):
    '''dummy_attribute_item : decl_modifiers BOOLEAN T_STRING boolean '''
    # { mi_api_release($3); }

def p_dummy_attribute_item_2(p):
    '''dummy_attribute_item : decl_modifiers INTEGER T_STRING T_INTEGER '''
    # { mi_api_release($3); }

def p_dummy_attribute_item_3(p):
    '''dummy_attribute_item : decl_modifiers SCALAR T_STRING floating '''
    # { mi_api_release($3); }

def p_dummy_attribute_item_4(p):
    '''dummy_attribute_item : decl_modifiers COLOR T_STRING floating floating floating floating '''
    # { mi_api_release($3); }

def p_dummy_attribute_item_5(p):
    '''dummy_attribute_item : decl_modifiers VECTOR T_STRING floating floating floating '''
    # { mi_api_release($3); }

def p_dummy_attribute_item_6(p):
    '''dummy_attribute_item : decl_modifiers STRING T_STRING T_STRING '''
    # { mi_api_release($3);
    #                           mi_api_release($4); }

def p_opt_override_1(p):
    '''opt_override :  '''

def p_opt_override_2(p):
    '''opt_override : OVERRIDE '''

def p_decl_modifiers_1(p):
    '''decl_modifiers : decl_mod_list '''

def p_decl_mod_list_1(p):
    '''decl_mod_list : decl_mod_list decl_mod '''

def p_decl_mod_list_2(p):
    '''decl_mod_list : decl_mod '''

def p_decl_mod_1(p):
    '''decl_mod : CONST '''

def p_decl_mod_2(p):
    '''decl_mod : GLOBAL '''

def p_attr_flag_1(p):
    '''attr_flag : HIDE boolean '''

def p_attr_flag_2(p):
    '''attr_flag : VISIBLE boolean '''

def p_attr_flag_3(p):
    '''attr_flag : TRANSPARENCY T_INTEGER '''

def p_attr_flag_4(p):
    '''attr_flag : REFLECTION T_INTEGER '''

def p_attr_flag_5(p):
    '''attr_flag : REFRACTION T_INTEGER '''

def p_attr_flag_6(p):
    '''attr_flag : SHADOW boolean '''

def p_attr_flag_7(p):
    '''attr_flag : SHADOW T_INTEGER '''

def p_attr_flag_8(p):
    '''attr_flag : FINALGATHER boolean '''

def p_attr_flag_9(p):
    '''attr_flag : FINALGATHER T_INTEGER '''

def p_attr_flag_10(p):
    '''attr_flag : CAUSTIC boolean '''

def p_attr_flag_11(p):
    '''attr_flag : CAUSTIC T_INTEGER '''

def p_attr_flag_12(p):
    '''attr_flag : GLOBILLUM boolean '''

def p_attr_flag_13(p):
    '''attr_flag : GLOBILLUM T_INTEGER '''

def p_attr_flag_14(p):
    '''attr_flag : MOTION boolean '''

def p_attr_flag_15(p):
    '''attr_flag : FACE FRONT '''

def p_attr_flag_16(p):
    '''attr_flag : FACE BACK '''

def p_attr_flag_17(p):
    '''attr_flag : FACE BOTH '''

def p_attr_flag_18(p):
    '''attr_flag : SELECT boolean '''

def p_attr_flag_19(p):
    '''attr_flag : HULL boolean '''

def p_attr_flag_20(p):
    '''attr_flag : SHADOWMAP boolean '''

def p_attr_flag_21(p):
    '''attr_flag : TRACE boolean '''

def p_attr_flag_22(p):
    '''attr_flag : CAUSTIC '''

def p_attr_flag_23(p):
    '''attr_flag : GLOBILLUM '''

def p_attr_flag_24(p):
    '''attr_flag : FINALGATHER '''

def p_attr_flag_25(p):
    '''attr_flag : HARDWARE '''

def p_attr_flag_26(p):
    '''attr_flag : HARDWARE boolean '''

def p_attr_flag_27(p):
    '''attr_flag : TAG T_INTEGER '''

def p_gui_1(p):
    '''gui : GUI opt_symbol _embed0_gui '(' gui_attr_list ')' '{' gui_controls '}' '''
    # { mi_api_gui_end(); }

def p_gui_2(p):
    '''gui : GUI opt_symbol _embed1_gui '{' gui_controls '}' '''
    # { mi_api_gui_end(); }

def p__embed0_gui(p):
    '''_embed0_gui : '''
    # { mi_api_gui_begin($2); }

def p__embed1_gui(p):
    '''_embed1_gui : '''
    # { mi_api_gui_begin($2); }

def p_gui_elems_1(p):
    '''gui_elems :  '''

def p_gui_elems_2(p):
    '''gui_elems : gui_elem gui_elems '''

def p_gui_elem_1(p):
    '''gui_elem : '(' gui_attr_list ')' '''

def p_gui_elem_2(p):
    '''gui_elem : '{' _embed0_gui_elem gui_controls '}' '''
    # { mi_api_gui_pop(); }

def p__embed0_gui_elem(p):
    '''_embed0_gui_elem : '''
    # { mi_api_gui_push(); }

def p_gui_controls_1(p):
    '''gui_controls :  '''

def p_gui_controls_2(p):
    '''gui_controls : gui_control gui_controls '''

def p_gui_control_1(p):
    '''gui_control : CONTROL symbol opt_symbol _embed0_gui_control gui_elems '''
    # { mi_api_gui_control_end(); }

def p__embed0_gui_control(p):
    '''_embed0_gui_control : '''
    # { mi_api_gui_control_begin($3?$2:0, $3?$3:$2); }

def p_gui_attr_list_1(p):
    '''gui_attr_list :  '''

def p_gui_attr_list_2(p):
    '''gui_attr_list : ',' '''

def p_gui_attr_list_3(p):
    '''gui_attr_list : gui_attr '''

def p_gui_attr_list_4(p):
    '''gui_attr_list : gui_attr ',' gui_attr_list '''

def p_gui_attr_1(p):
    '''gui_attr : symbol '''
    # { mi_api_gui_attr($1, miNTYPES, 0); }

def p_gui_attr_2(p):
    '''gui_attr : symbol boolean '''
    # { mi_api_gui_attr($1, miTYPE_BOOLEAN, 1, $2); }

def p_gui_attr_3(p):
    '''gui_attr : symbol floating '''
    # { mi_api_gui_attr($1, miTYPE_SCALAR, 1, $2); }

def p_gui_attr_4(p):
    '''gui_attr : symbol floating floating '''
    # { mi_api_gui_attr($1, miTYPE_SCALAR, 2, $2, $3); }

def p_gui_attr_5(p):
    '''gui_attr : symbol floating floating floating '''
    # { mi_api_gui_attr($1, miTYPE_SCALAR, 3, $2, $3, $4); }

def p_gui_attr_6(p):
    '''gui_attr : symbol floating floating floating floating '''
    # { mi_api_gui_attr($1, miTYPE_SCALAR, 4, $2,$3,$4,$5); }

def p_gui_attr_7(p):
    '''gui_attr : symbol symbol '''
    # { mi_api_gui_attr($1, miTYPE_STRING, 1, $2); }

def p_command_include1(p):
	'''command : INCLUDE INCPATH '''
	pass
	
def p_command_include2(p):
	'''command : INCLUDE T_STRING '''
	pass


def _add_decorators():
    """
    loop through functions in this module and applies the 'flag' decorator to those whose names start
    with 'p_' and contain 'flag' or 'item' in their names.
    """
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module):
        if re.match( 'p_.*_(flag|item)_\d+$', name ):
            doc = func.__doc__
            type, rules = _split_rule(doc)
            if len(rules) and rules[0].isupper():
                if debug:
                    print "fixing", name, rules

                setattr( module, name, flag(func) )

_add_decorators()
	
# -------------- RULES END ----------------

lexer = lex.lex(module=mi_lexer)
lexer.root = None
parser = yacc.yacc()

if __name__ == '__main__':
    from ply import *
    yacc.yacc()

