%start start

%union {
        miBoolean     boolean;
        char          *symbol;
        char          *string;
        struct {
                int       len;
                miUchar   *bytes;
        }             byte_string;
        int           integer;
        double        floating;
        float         floatoctet[8];
        miMatrix      matrix;
        miColor       color;
        miVector      vector;
        miGeoVector   geovector;
        miTransform   *transform;
        miParameter   *para_type;
        miDlist       *dlist;
        miTag         tag;
}
 
%token <symbol>         T_SYMBOL
%token <integer>        T_INTEGER
%token <floating>       T_FLOAT
%token <string>         T_STRING
%token <byte_string>    T_BYTE_STRING
%token <vector>         T_VECTOR

%token AMBIENTOCCLUSION ACCELERATION ACCURACY ADAPTIVE ALL ALPHA ANGLE ANY 
%token APERTURE APPLY
%token APPROXIMATE ARRAY ASPECT ASSEMBLY ATTRIBUTE AUTOVOLUME
%token B BACK BASIS BEZIER BIAS BINARY BLUE BOOLEAN BORDER BOTH BOX BSDF
%token BSP BSP2 BSPLINE BUFFER BUMP
%token CALL CAMERA CARDINAL CAUSTIC CCMESH CG CHILD
%token CLASSIFICATION CLIP CODE COLLECT COLOR COLORCLIP COLORPROFILE
%token COMPRESS COMPRESSION CONE
%token CONIC CONNECT CONST_ CONSTANT CONTOUR CONTRAST CONTROL CORNER CP CREASE
%token CURVATURE CURVE CUSP CYLINDER
%token D D2 DART DATA DATATYPE DEBUG_ DECLARE DEFAULT DEGREE DELAUNAY DELETE_ DENSITY
%token DEPTH DERIVATIVE DESATURATE DETAIL DIAGNOSTIC DIRECTION DISC DISPLACE
%token DISTANCE DITHER DOD DOF DPI
%token ECHO EMITTER END ENVIRONMENT EVEN ENERGY EULUMDAT EXPONENT
%token FACE FALLOFF FALSE_ FAN FAST FASTLOOKUP FIELD FILENAME FILETYPE
%token FILE_ FILTER FILTERING FINALGATHER FINE FLAGS FOCAL
%token FORCE FORMAT FRAGMENT FRAME FRAMEBUFFER FREEZE FRONT
%token GAMMA GAUSS GEOMETRY GLOBAL GLOBILLUM GRADING GREEN GRID GROUP GUI
%token HAIR HARDWARE HERMITE HIDE HOLE HULL
%token IBL IES IMP IMPLICIT IMPORTANCE INCREMENTAL INFINITY_ INHERITANCE INSTANCE 
%token INSTGROUP INTEGER INTERFACE_ INTERSECTION IRRADIANCE
%token JITTER
%token LANCZOS LARGE LENGTH LENS LEVEL LIGHT LIGHTMAP LIGHTPROFILE LINK LOCAL
%token LUMINANCE
%token M MAPSTO MASK MATERIAL MATRIX MAX_ MEMORY MERGE MI_ MIN_ MITCHELL MIXED
%token MOTION
%token N NAMESPACE NATIVE NOCONTOUR NOSMOOTHING NORMAL NULL_ NTSC
%token OBJECT ODD OFF OFFSET OFFSCREEN ON ONLY OPAQUE_ OPENGL OPTIONS ORIGIN
%token OUTPUT OVERRIDE
%token P_ PARALLEL_ PARAMETRIC PASS PHENOMENON PHOTON PHOTONMAP PHOTONS
%token PHOTONVOL POLYGON POSITION PREMULTIPLY PREP PRESAMPLE PRIMARY PRIORITY PRIVATE
%token PROTOCOL
%token QUALITY
%token RADIUS RAPID RAST RATIONAL RAY_ RAYCL RAW READ REBUILD RECTANGLE RECURSIVE
%token RED REFLECTION REFRACTION REGISTRY REGULAR
%token RENDER RESOLUTION RGB_ ROOT
%token SAMPLELOCK SAMPLES SCALE SCALAR SCANLINE SECONDARY SEGMENTS SELECT SESSION
%token SET SHADER SHADING SHADOW SHADOWMAP SHARP SHUTTER SIZE SOFTNESS SORT SPACE
%token SPATIAL SPDL SPECIAL SPECTRUM SPHERE SPREAD STATE STEPS STORE STRING
%token STRIP STRUCT 
%token SUBDIVISION SURFACE SYSTEM
%token T_ TAG TAGGED TASK TAYLOR TEXTURE TIME TOPOLOGY TOUCH TRACE TRANSFORM
%token TRANSPARENCY TRAVERSAL TREE TRIANGLE TRILIST TRIM TRUE_
%token U_ UNIFORM USEOPACITY USEPRIMARY USER
%token V_ VALUE VECTOR VENDOR VERBOSE VERSION VERTEX VIEW VISIBLE VOLUME
%token W_ WEIGHT WHITE WIDTH WINDOW WORLD WRITABLE WRITE

%type <floating>   foating
%type <boolean>    boolean
%type <string>     symbol
%type <string>     opt_symbol
%type <matrix>     transform
%type <integer>    tex_flags
%type <integer>    tex_flag
%type <integer>    tex_type
%type <integer>    simple_type
%type <string>     inst_item
%type <tag>        inst_func
%type <tag>        inst_params
%type <tag>        function
%type <tag>        function_list
%type <tag>        function_array
%type <tag>        tex_func_list
%type <tag>        phen_root
%type <para_type>       shret_type
%type <para_type>       shret_type_nosh
%type <para_type>       shret_decl_seq
%type <para_type>       shret_decl
%type <para_type>       decl_simple
%type <para_type>       parm_decl_list
%type <para_type>       parm_decl_seq
%type <para_type>       parm_decl
%type <vector>    vector
%type <integer>   apply
%type <integer>   apply_list
%type <integer>   filter_type
%type <string>    colorspace_set
%type <color>     color
%type <boolean>   incl_excl
%type <tag>       light_list         
                                                        /* smallparser_begin */
%type <tag>       opt_function_list
%type <string>    opt_string
%type <integer>   colorclip_mode
%type <geovector> geovector
%type <string>    mtl_or_label
%type <boolean>   rational
%type <dlist>     basis_matrix
%type <floating>  merge_option
%type <dlist>     para_list
%type <boolean>   opt_volume_flag
%type <boolean>   opt_vector_flag
%type <boolean>   opt_incremental
%type <floatoctet>      out_parms
%type <integer>   c_filter_type
%type <integer>   pass_samples
%type <dlist>     string_list
%type <dlist>     map_list
%type <integer>   opt_size
%type <integer>   pl_border
                                                          /* smallparser_end */

%%

start           :
                        { functag = 0;
                          mi_api_incremental(is_incremental = miFALSE);
                          mi_api_private(session_depth = 0);
                          my_timer = mi_timing(0, 0); }
                  command_list
                        { mi_timing(my_timer, 0); }
                |
                ;


/*-----------------------------------------------------------------------------
 * primitive types
 *---------------------------------------------------------------------------*/

boolean         : ON
                        { $$ = miTRUE; }
                | OFF
                        { $$ = miFALSE; }
                | TRUE_
                        { $$ = miTRUE; }
                | FALSE_
                        { $$ = miFALSE; }
                ;

floating        : T_FLOAT       { $$ = $1; }
                | T_INTEGER     { $$ = $1; }
                ;

vector          : floating floating floating
                        { $$.x = $1; $$.y = $2; $$.z = $3; }
                | T_VECTOR
                        { $$ = $1; }
                ;

                                                        /* smallparser_begin */
geovector       : floating floating floating
                        { $$.x = $1; $$.y = $2; $$.z = $3; }
                | T_VECTOR
                        { $$.z = $1.z; $$.y = $1.y; $$.x = $1.x; }
                ;
                                                          /* smallparser_end */

color           : floating floating floating
                        { $$.r = $1; $$.g = $2; $$.b = $3; $$.a = 1.0f; }
                | floating floating floating floating
                        { $$.r = $1; $$.g = $2; $$.b = $3; $$.a = $4; }
 
                ;

transform       : TRANSFORM     floating floating floating floating
                                floating floating floating floating
                                floating floating floating floating
                                floating floating floating floating
                        { $$[0] = $2;  $$[1] = $3;  $$[2] = $4;  $$[3] = $5;
                          $$[4] = $6;  $$[5] = $7;  $$[6] = $8;  $$[7] = $9;
                          $$[8] = $10; $$[9] = $11; $$[10]= $12; $$[11]= $13;
                          $$[12]= $14; $$[13]= $15; $$[14]= $16; $$[15]= $17; }
                ;

symbol          : T_SYMBOL
                        { $$ = $1; }
                | T_STRING
                        { $$ = $1; }
                ;

opt_symbol      :
                        { $$ = 0; }
                | symbol
                        { $$ = $1; }
                ;

                                                        /* smallparser_begin */
opt_string      :
                        { $$ = 0; }
                | T_STRING
                        { $$ = $1; }
                ;

colorclip_mode  :  RGB_
                        { $$ = miIMG_COLORCLIP_RGB; }
                |  ALPHA
                        { $$ = miIMG_COLORCLIP_ALPHA; }
                |  RAW
                        { $$ = miIMG_COLORCLIP_RAW; }
                ;
                                                          /* smallparser_end */


/*-----------------------------------------------------------------------------
 * top-level commands
 *---------------------------------------------------------------------------*/

command_list    :       { mi_api_incremental(is_incremental = miFALSE);
                          mi_api_private(session_depth = 0); }
                  command
                | command_list
                        { mi_api_incremental(is_incremental = miFALSE);
                          mi_api_private(session_depth = 0); }
                  command
                ;

command         : set
                                                        /* smallparser_begin */
                | frame
                | debug
                | call
                                                          /* smallparser_end */
                | version
                | incr_command
                | PRIVATE
                        { mi_api_private(session_depth = 255); }
                  incr_command
                | SESSION DEPTH T_INTEGER
                        { mi_api_private(session_depth = $3); }
                  incr_command
                | INCREMENTAL
                        { mi_api_incremental(is_incremental = miTRUE);
                          mi_api_private(session_depth = 0); }
                  incr_command
                                                        /* smallparser_begin */
                | DELETE_ symbol
                        { mi_api_delete($2); }
                | RENDER symbol symbol symbol
                        { mi_timing(my_timer, "mi scene file parsing");
                          mi_timing(my_timer, 0);
                          mi_api_render($2, $3, $4,
                                         mi_api_strdup(ctx->inheritance_func));
                          yyreturn MIYYRENDER; }
                                                          /* smallparser_end */
                | VERBOSE boolean
                        { if (!ctx->mi_force_verbose)
                                mi_set_verbosity($2? miERR_ALL & ~miERR_DEBUG
                                                               & ~miERR_VDEBUG
                                                   : miERR_FATAL|miERR_ERROR);}
                | VERBOSE T_INTEGER
                        { if (!ctx->mi_force_verbose)
                                mi_set_verbosity((1 << $2) - 1); }
                | ECHO T_STRING
                        { mi_info("%s", $2);
                          mi_api_release($2); }
                | SYSTEM T_STRING
                        { if ((system($2) >> 8) & 0xff)
                          mi_api_warning("system \"%s\" failed", $2);
                          mi_api_release($2); }
                | MEMORY T_INTEGER
                        { mi_api_warning("memory view parameter ignored"); }
                | CODE T_STRING
                        { mi_link_file_add($2, miTRUE, miFALSE, miFALSE);
                          mi_api_release($2); }
                | CODE
                        { mi_api_code_verbatim_begin(); }
                  code_bytes_list
                        { mi_api_code_verbatim_end(); }
                | LINK T_STRING
                        { mi_link_file_add($2, miFALSE, miFALSE, miFALSE);
                          mi_api_release($2); }
                | DECLARE function_decl
                | DECLARE phenomenon_decl
                | DECLARE data_decl
                | REGISTRY symbol
                        { mi_api_registry_begin($2); }
                  reg_body END REGISTRY
                        { mi_api_registry_end(); }
                | TOUCH symbol
                        { mi_api_touch($2); }
                | NAMESPACE symbol
                        { mi_api_scope_begin($2); }
                | END NAMESPACE
                        { mi_api_scope_end(); }
                | ROOT symbol
                        { mi_api_assembly_root($2); }
                ;

reg_body        :
                | reg_item reg_body
                ;

reg_item        : VALUE symbol
                        { mi_api_registry_add(mi_api_strdup("value"), $2); }
                | LINK symbol
                        { mi_api_registry_add(mi_api_strdup("link"), $2); }
                | CODE symbol
                        { mi_api_registry_add(mi_api_strdup("code"), $2); }
                | MI_ symbol
                        { mi_api_registry_add(mi_api_strdup("mi"), $2); }
                | SPDL symbol
                        { mi_api_registry_add(mi_api_strdup("spdl"), $2); }
                | ECHO symbol
                        { mi_api_registry_add(mi_api_strdup("echo"), $2); }
                | SYSTEM symbol
                        { mi_api_registry_add(mi_api_strdup("system"), $2); }
                | symbol symbol
                        { mi_api_registry_add($1, $2); }
                ;

incr_command    : light
                | instance
                                                        /* smallparser_begin */
                | options
                | camera
                | object
                                                          /* smallparser_end */
                | texture
                | profile_data
                | cprof
                | spectrum_data
                | material
                | instgroup
                | assembly
                | userdata
                | gui
                | SHADER symbol function_list
                        { mi_api_shader_add($2, $3); }
                ;

code_bytes_list : T_BYTE_STRING
                        { mi_api_code_byte_copy($1.len, $1.bytes); }
                | code_bytes_list T_BYTE_STRING
                        { mi_api_code_byte_copy($2.len, $2.bytes); }
                ;

set             : SET symbol
                        { mi_api_variable_set($2, 0); }
                | SET symbol symbol
                        { mi_api_variable_set($2, $3); }
                ;

                                                        /* smallparser_begin */
call            : CALL function_list
                        { mi_api_shader_call($2, 0, 0); }
                | CALL function_list ',' symbol symbol
                        { mi_api_shader_call($2, $4, $5); }
                ;

debug           : DEBUG_ symbol opt_symbol
                        { mi_api_debug($2, $3); }
                                                          /* smallparser_end */
                ;

version         : VERSION T_STRING
                        { mi_api_version_check($2, 0); }
                | MIN_ VERSION T_STRING
                        { mi_api_version_check($3, 0); }
                | MAX_ VERSION T_STRING
                        { mi_api_version_check($3, 1); }
                ;


                                                        /* smallparser_begin */
/*****************************************************************************
 *************************    mi1 compatibility    ***************************
 *****************************************************************************/

/*-----------------------------------------------------------------------------
 * frame
 *---------------------------------------------------------------------------*/

frame           :
                        { mi_api_frame_begin(&camera, &options); }
                  frame_number
                  initial_frame_cmd_list
                  view
                  frame_command_list
                  END FRAME
                        { mi_timing(my_timer, "mi scene file parsing");
                          mi_timing(my_timer, 0);
                          mi_api_frame_end();
                          yyreturn MIYYENDFRAME; }
                ;

initial_frame_cmd_list
                :
                | initial_frame_cmd_list initial_frame_cmd
                ;

initial_frame_cmd
                : texture
                | light
                | material
                ;

frame_command_list
                :
                | frame_command_list frame_command
                ;

frame_command
                : texture
                | light
                | material
                | object
                | call
                | debug
                | version
                | gui
                ;


/*-----------------------------------------------------------------------------
 * view
 *---------------------------------------------------------------------------*/

view            : VIEW
                          {
                            have_l = have_v = have_e = have_p = 0;
                            if (is_incremental == miFALSE) {
                                mi_api_function_delete(&camera->output);
                                Edit_fb fb(camera->buffertag);
                                fb->reset();
                            }
                          }
                  view_list
                  END VIEW
                ;

view_list       :
                | view_list view_item
                ;

view_item       : camview_item
                | optview_item
                | MIN_ SAMPLES T_INTEGER
                        { options->min_samples = $3; }
                | MAX_ SAMPLES T_INTEGER
                        { options->max_samples = $3; }
                | SAMPLES T_INTEGER
                        { mi_api_warning(
                                "\"samples\" view parameter ignored"); }
                | RECURSIVE boolean
                        { if (!$2)
                                mi_api_warning("\"recursive off\" ignored"); }
                | ADAPTIVE boolean
                        { mi_api_warning("\"adaptive\" statement ignored"); }
                | ACCELERATION RAY_ CLASSIFICATION
                        { options->acceleration = 'b';
                          mi_api_warning(
                                "ray classification is obsolete, using BSP"); }
                | ACCELERATION SPATIAL SUBDIVISION
                        { options->acceleration = 'b'; }
                | ACCELERATION GRID
                        { options->acceleration = 'g'; }
                | SUBDIVISION MEMORY T_INTEGER
                        { mi_api_warning("ray classification is obsolete, "
                          "statement \"subdivision memory %d\" ignored", $3); }
                | SUBDIVISION T_INTEGER T_INTEGER
                        { mi_api_warning("ray classification is obsolete, "
                          "statement \"subdivision %d %d\" ignored", $2, $3); }
                | MAX_ SIZE T_INTEGER
                        { options->space_max_size = $3; }
                | MAX_ DEPTH T_INTEGER
                        { options->space_max_depth = $3; }
                | SHADOW SORT boolean
                        { if ($3) options->shadow = 'l'; }
                | SHADOW SEGMENTS boolean
                        { if ($3) options->shadow = 's'; }
                | transform
                        { mi_api_view_transform($1); }
                | RED floating floating
                | GREEN floating floating
                | BLUE floating floating
                | WHITE floating floating
                ;
                                                          /* smallparser_end */


/*****************************************************************************
 *************************    new mi2 features    ****************************
 *****************************************************************************/

/*-----------------------------------------------------------------------------
 * options
 *---------------------------------------------------------------------------*/

                                                        /* smallparser_begin */
options         : OPTIONS symbol
                    {
                        options = mi_api_options_begin($2);
                        iface = mi_get_shader_interface();
                        string_options = iface->getOptions(options->string_options);
                        iface->release();
                        iface = 0;
                        have_pm = miFALSE; 
                        have_sf = 0;
                    }
                  option_list END OPTIONS
                        { string_options->release();
                          string_options = 0;
                          mi_api_options_end(); }
                ;

option_list     :
                | option_list option_item
                ;

option_item     : optview_item
                | string_option_item
                |       { curr_datatag = &options->userdata; }
                  data
                | ACCELERATION RAYCL
                        { options->acceleration = 'b';
                          mi_api_warning(
                                "ray classification is obsolete, using BSP"); }
                | ACCELERATION BSP
                        { options->acceleration = 'b'; }
                | ACCELERATION BSP2
                        { options->acceleration = 'n'; }
                | ACCELERATION LARGE BSP
                        { options->acceleration = 'l'; }
                | ACCELERATION GRID
                        { options->acceleration = 'g'; }
                | MOTION boolean
                        { if ($2) options->motion = 1; }
                | MOTION STEPS T_INTEGER
                        { options->n_motion_vectors = $3;}
                | DIAGNOSTIC SAMPLES boolean
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_SAMPLES,$3);}
                | DIAGNOSTIC PHOTON OFF
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_PHOTON, miFALSE);}
                | DIAGNOSTIC PHOTON DENSITY floating
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_PHOTON, miFALSE);
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_PHOTON_D, miTRUE);
                          options->diag_photon_density = $4;}
                | DIAGNOSTIC PHOTON IRRADIANCE floating
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_PHOTON, miFALSE);
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_PHOTON_I, miTRUE);
                          options->diag_photon_density = $4;}
                | DIAGNOSTIC GRID OFF
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID, miFALSE);}
                | DIAGNOSTIC GRID OBJECT floating
                        { options->diag_grid_size = $4;
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID, miFALSE);
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID_O, $4 != 0.0);}
                | DIAGNOSTIC GRID WORLD floating
                        { options->diag_grid_size = $4;
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID, miFALSE);
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID_W, $4 != 0.0);}
                | DIAGNOSTIC GRID CAMERA floating
                        { options->diag_grid_size = $4;
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID, miFALSE);
                          miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_GRID_C, $4 != 0.0);}
                | DIAGNOSTIC BSP OFF
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_BSP, miFALSE); }
                | DIAGNOSTIC BSP DEPTH
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_BSP_D, miTRUE); }
                | DIAGNOSTIC BSP SIZE
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_BSP_L, miTRUE); }
                | DIAGNOSTIC FINALGATHER boolean
                        { miBIT_SWITCH(options->diagnostic_mode,
                                miSCENE_DIAG_FG, $3);}
                                                        /* hardware_begin */
                | DIAGNOSTIC HARDWARE boolean
                        { miBIT_SWITCH(options->hardware_diagnostic,
                                miSCENE_HWDIAG_SOLID, $3); }
                | DIAGNOSTIC HARDWARE GRID
                        { miBIT_SWITCH(options->hardware_diagnostic,
                                miSCENE_HWDIAG_WIRE, miTRUE); }
                | DIAGNOSTIC HARDWARE WINDOW
                        { miBIT_SWITCH(options->hardware_diagnostic,
                                        miSCENE_HWDIAG_WINDOW, miTRUE); }
                | DIAGNOSTIC HARDWARE LIGHT
                        { miBIT_SWITCH(options->hardware_diagnostic,
                                miSCENE_HWDIAG_LIGHTS, miTRUE); }
                                                        /* hardware_end */
                | SAMPLES T_INTEGER
                        { options->min_samples = $2-2;
                          options->max_samples = $2; }
                | SAMPLES T_INTEGER T_INTEGER
                        { options->min_samples = $2;
                          options->max_samples = $3; }
                | SAMPLES T_INTEGER T_INTEGER T_INTEGER T_INTEGER
                        { options->min_samples = $2;
                          options->max_samples = $3;
                          options->def_min_samples = $4;
                          options->def_max_samples = $5; }
                | SAMPLES COLLECT T_INTEGER
                        { if ($3 > 0)
                                options->rast_collect_rate = $3;
                          else if ($3 < 0)
                                mi_warning("invalid negative \"samples"
                                           " collect %d\" has been ignored.",
                                           $3);
                        }
                | SAMPLES MOTION T_INTEGER
                        { options->rast_motion_resample = $3; }
                | SHADOW SORT
                        { options->shadow = 'l'; }
                | SHADOW SEGMENTS
                        { options->shadow = 's'; }
                | COLORPROFILE symbol 
                        { options->render_cprof = mi_api_name_lookup($2); }
                | options_attribute     
                ;

optview_item    : SHADOW OFF
                        { options->shadow = 0; }
                | SHADOW ON
                        { options->shadow = 1; }
                | TRACE boolean
                        { options->trace = $2; }
                | SCANLINE boolean
                        { options->scanline = $2; }
                | SCANLINE RAST
                        { options->scanline = 'r'; }
                | SCANLINE RAPID
                        { options->scanline = 'r'; }
                | SCANLINE OPENGL
                        { options->scanline = 'o'; }
                                                        /* hardware_begin */
                | HARDWARE boolean
                        { options->hardware = $2 ? 1 : 0; }
                | HARDWARE ALL
                        { options->hardware = 3; }
                | HARDWARE FORCE
                        { options->hwshader |= 1; }
                | HARDWARE CG
                        { options->hwshader |= 2; }
                | HARDWARE NATIVE
                        { options->hwshader |= 4; }
                | HARDWARE FAST
                        { options->hwshader |= 8; }
                | HARDWARE SAMPLES T_INTEGER T_INTEGER
                        { hoptions = mi_rchw_get_options(); 
                          hoptions->multi_samples = $3;
                          hoptions->super_samples = $4; }
                                                        /* hardware_end */
                | LENS boolean
                        { options->no_lens = !$2; }
                | VOLUME boolean
                        { options->no_volume = !$2; }
                | GEOMETRY boolean
                        { options->no_geometry = !$2; }
                | DISPLACE boolean
                        { options->no_displace = !$2; }
                | DISPLACE PRESAMPLE boolean
                        { options->no_predisplace = !$3; }
                | OUTPUT boolean
                        { options->no_output = !$2; }
                | MERGE boolean
                        { options->no_merge = !$2; }
                | HAIR boolean
                        { options->no_hair = !$2; }
                | PASS boolean
                        { options->no_pass = !$2; }
                | AUTOVOLUME boolean
                        { options->autovolume = $2; }
                | PHOTON AUTOVOLUME boolean
                        { options->photon_autovolume = $3; }
                | FILTER filter_type
                        { options->filter     = $2;
                          options->filter_size_x =
                          options->filter_size_y = 0.0; }
                | FILTER filter_type floating
                        { options->filter     = $2;
                          options->filter_size_x =
                          options->filter_size_y = $3; }
                | FILTER filter_type floating floating
                        { options->filter     = $2;
                          options->filter_size_x = $3;
                          options->filter_size_y = $4; }
                | FACE FRONT
                        { options->face = 'f'; }
                | FACE BACK
                        { options->face = 'b'; }
                | FACE BOTH
                        { options->face = 'a'; }
                | FIELD OFF
                        { options->field = 0; }
                | FIELD EVEN
                        { options->field = 'e'; }
                | FIELD ODD
                        { options->field = 'o'; }
                | SAMPLELOCK boolean
                        { options->samplelock = $2; }
                | PHOTON TRACE DEPTH T_INTEGER
                        { options->photon_reflection_depth = $4;
                          options->photon_refraction_depth = $4;
                          options->photon_trace_depth           = $4 + $4; }
                | PHOTON TRACE DEPTH T_INTEGER T_INTEGER
                        { options->photon_reflection_depth = $4;
                          options->photon_refraction_depth = $5;
                          options->photon_trace_depth           = $4 + $5; }
                | PHOTON TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER
                        { options->photon_reflection_depth = $4;
                          options->photon_refraction_depth = $5;
                          options->photon_trace_depth           = $6; }
                | FINALGATHER TRACE DEPTH T_INTEGER
                        { options->fg_reflection_depth =
                          options->fg_refraction_depth = $4;
                          options->fg_diffuse_depth    =
                          options->fg_trace_depth      = $4 + $4; }
                | FINALGATHER TRACE DEPTH T_INTEGER T_INTEGER
                        { options->fg_reflection_depth = $4;
                          options->fg_refraction_depth = $5;
                          options->fg_diffuse_depth    =
                          options->fg_trace_depth      = $4 + $5; }
                | FINALGATHER TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER
                        { options->fg_reflection_depth = $4;
                          options->fg_refraction_depth = $5;
                          options->fg_diffuse_depth    =
                          options->fg_trace_depth      = $6; }
                | FINALGATHER TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER T_INTEGER
                        { options->fg_reflection_depth = $4;
                          options->fg_refraction_depth = $5;
                          options->fg_diffuse_depth    = $6; 
                          options->fg_trace_depth      = $7; }
                | TRACE DEPTH T_INTEGER
                        { options->reflection_depth = $3;
                          options->refraction_depth = $3;
                          options->trace_depth           = $3 + $3; }
                | TRACE DEPTH T_INTEGER T_INTEGER
                        { options->reflection_depth = $3;
                          options->refraction_depth = $4;
                          options->trace_depth           = $3 + $4; }
                | TRACE DEPTH T_INTEGER T_INTEGER T_INTEGER
                        { options->reflection_depth  = $3;
                          options->refraction_depth  = $4;
                          options->trace_depth       = $5; }
                | CONTRAST floating floating floating
                        { options->contrast.r = $2;
                          options->contrast.g = $3;
                          options->contrast.b = $4;
                          options->contrast.a = ($2 + $3 + $4)/3; }
                | CONTRAST floating floating floating floating
                        { options->contrast.r = $2;
                          options->contrast.g = $3;
                          options->contrast.b = $4;
                          options->contrast.a = $5; }
                | TIME CONTRAST floating floating floating
                        { options->time_contrast.r = $3;
                          options->time_contrast.g = $4;
                          options->time_contrast.b = $5;
                          options->time_contrast.a = ($3 + $4 + $5)/3; }
                | TIME CONTRAST floating floating floating floating
                        { options->time_contrast.r = $3;
                          options->time_contrast.g = $4;
                          options->time_contrast.b = $5;
                          options->time_contrast.a = $6; }
                | CONTOUR STORE function
                        { options->contour_store = $3; }
                | CONTOUR CONTRAST function
                        { options->contour_contrast = $3; }
                | STATE function
                        {
                            if (!have_sf++)
                                mi_api_function_delete(&options->state_func);
                            options->state_func = mi_api_function_append(options->state_func, $2);
                        }
                | STATE function_array
                        {
                            if ($2 != miNULLTAG) {
                                if (!have_sf++)
                                    mi_api_function_delete(&options->state_func);
                                options->state_func = mi_api_function_append(
                                                                options->state_func, $2);
                            } else {
                                mi_api_function_delete(&options->state_func);
                                have_sf = 0;
                            }
                        }
                | JITTER floating
                        { options->jitter     = $2; }
                | SHUTTER floating
                        { options->shutter    = $2;
                          options->motion     = options->shutter > 0; }
                | SHUTTER floating floating
                        { options->shutter_delay = $2;
                          options->shutter    = $3;
                          options->motion     = options->shutter > 0; }
                | TASK SIZE T_INTEGER
                        { options->task_size = $3; }
                | RAYCL SUBDIVISION T_INTEGER T_INTEGER
                        { mi_api_warning("ray classification is obsolete, "
                          "statement \"raycl subdivision %d %d\" ignored",
                                                                $3, $4); }
                | RAYCL MEMORY T_INTEGER
                        { mi_api_warning("ray classification is obsolete, "
                          "statement \"raycl memory %d\" ignored", $3); }
                | BSP SIZE T_INTEGER
                        { options->space_max_size = $3; }
                | BSP DEPTH T_INTEGER
                        { options->space_max_depth = $3; }
                | BSP MEMORY T_INTEGER
                        { options->space_max_mem = $3; }
                | BSP SHADOW boolean
                        { options->space_shadow_separate = $3; }
                | GRID SIZE T_INTEGER
                        { options->grid_max_size = $3; }
                | GRID SIZE T_FLOAT
                        { options->grid_res[0] =
                          options->grid_res[1] =
                          options->grid_res[2] = (int)$3;
                          mi_api_warning("obsolete grid size statement, "
                                "use grid resolution instead"); }
                | GRID RESOLUTION T_INTEGER
                        { options->grid_res[0] =
                          options->grid_res[1] =
                          options->grid_res[2] = $3; }
                | GRID RESOLUTION T_INTEGER T_INTEGER T_INTEGER
                        { options->grid_res[0] = $3;
                          options->grid_res[1] = $4;
                          options->grid_res[2] = $5; }
                | GRID DEPTH T_INTEGER
                        { options->grid_max_depth = $3; }
                | DESATURATE boolean
                        { options->desaturate = $2; }
                | DITHER boolean
                        { options->dither = $2; }
                | PREMULTIPLY boolean
                        { options->nopremult = !$2; }
                | COLORCLIP colorclip_mode
                        { options->colorclip = $2; }
                | GAMMA floating
                        { options->gamma = $2; }
                | OBJECT SPACE
                        { options->render_space = 'o'; }
                | CAMERA SPACE
                        { options->render_space = 'c'; }
                | MIXED SPACE
                        { options->render_space = 'm'; }
                | WORLD SPACE
                        { mi_api_warning(
                                "world space statement ignored"); } /*<<<*/
                | INHERITANCE symbol
                        { options->inh_is_traversal = miFALSE;
                          if (ctx->inheritance_func)
                                mi_api_release(ctx->inheritance_func);
                          ctx->inheritance_func = $2;
                          if (!(options->inh_funcdecl = mi_api_decl_lookup(
                                                           mi_api_strdup($2))))
                                mi_api_nerror(176, "undeclared inheritance "
                                                          "shader \"%s\"", $2);
                        }
                | TRAVERSAL symbol
                        { options->inh_is_traversal = miTRUE;
                          if (ctx->inheritance_func)
                                mi_api_release(ctx->inheritance_func);
                          ctx->inheritance_func = $2;
                          if (!(options->inh_funcdecl = mi_api_decl_lookup(
                                                           mi_api_strdup($2))))
                                mi_api_nerror(177, "undeclared traversal "
                                                          "shader \"%s\"", $2);
                        }
                | SHADING SAMPLES floating
                        { options->rast_shading_samples = $3; }
                | SHADOWMAP MOTION boolean
                        { options->shadow_map_motion = $3; }
                | SHADOWMAP REBUILD boolean
                        { options->recompute_shadow_maps = (($3)?'y':'n');
                          options->shadowmap_flags &= ~miSHADOWMAP_MERGE; }
                | SHADOWMAP REBUILD MERGE
                        { options->recompute_shadow_maps = 'm';
                          options->shadowmap_flags |= miSHADOWMAP_MERGE; }
                | SHADOWMAP boolean
                        { options->use_shadow_maps &= 0x80;
                          options->shadowmap_flags &= ~miSHADOWMAP_DETAIL;
                          if ($2) options->use_shadow_maps |= 1;
                          else    options->use_shadow_maps  = 0; }
                | SHADOWMAP OPENGL
                        { options->use_shadow_maps &= 0x80;
                          options->use_shadow_maps |= 'o'; }
                | SHADOWMAP TRACE
                        { options->shadowmap_flags |= miSHADOWMAP_TRACE; }
                | SHADOWMAP TRACE boolean
                        { if ($3)
                                options->shadowmap_flags |= miSHADOWMAP_TRACE;
                          else
                                options->shadowmap_flags &=~miSHADOWMAP_TRACE;}
                | SHADOWMAP WINDOW
                        { options->shadowmap_flags |= miSHADOWMAP_CROP; }
                | SHADOWMAP WINDOW boolean
                        { if ($3)
                                options->shadowmap_flags |= miSHADOWMAP_CROP;
                          else
                                options->shadowmap_flags &= ~miSHADOWMAP_CROP;}
                | SHADOWMAP ONLY
                        { options->use_shadow_maps |= 0x80;
                          options->shadowmap_flags |= miSHADOWMAP_ONLY; }
                | SHADOWMAP DETAIL
                        { options->use_shadow_maps &= 0x80;
                          options->use_shadow_maps |= 'd';
                          options->shadowmap_flags |= miSHADOWMAP_DETAIL; }
                | SHADOWMAP BIAS floating
                        { options->shadowmap_bias = $3; }
                | LIGHTMAP boolean 
                        { options->lightmap = $2 ? miLIGHTMAP_ON 
                                                 : miLIGHTMAP_OFF; }
                | LIGHTMAP ONLY
                        { options->lightmap = miLIGHTMAP_ONLY; } 
                | CAUSTIC boolean
                        { options->caustic = $2; }
                | CAUSTIC T_INTEGER
                        { options->caustic_flag = $2; }
                | CAUSTIC ACCURACY T_INTEGER
                        { options->caustic_accuracy = $3; }
                | CAUSTIC ACCURACY T_INTEGER floating
                        { options->caustic_accuracy = $3;
                          options->caustic_radius = $4; }
                | CAUSTIC FILTER c_filter_type
                        { options->caustic_filter = $3;
                          options->caustic_filter_const = 1.1; }
                | CAUSTIC FILTER c_filter_type floating
                        { options->caustic_filter = $3;
                          options->caustic_filter_const = $4; }
                | CAUSTIC SCALE color
                        { options->caustic_scale = $3; }  
                | GLOBILLUM boolean
                        { options->globillum = $2; }
                | GLOBILLUM T_INTEGER
                        { options->globillum_flag = $2; }
                | GLOBILLUM ACCURACY T_INTEGER
                        { options->globillum_accuracy = $3; }
                | GLOBILLUM ACCURACY T_INTEGER floating
                        { options->globillum_accuracy = $3;
                          options->globillum_radius = $4; }
                | GLOBILLUM SCALE color
                        { options->globillum_scale = $3; } 
                | FINALGATHER boolean
                        { options->finalgather = $2; }
                | FINALGATHER FASTLOOKUP
                        { options->finalgather = 'f'; }
                | FINALGATHER ONLY
                        { options->finalgather = 'o'; }
                | FINALGATHER ACCURACY T_INTEGER
                        { options->finalgather_view      = miFALSE;
                          options->finalgather_rays      = $3; }
                | FINALGATHER ACCURACY T_INTEGER floating
                        { options->finalgather_view      = miFALSE;
                          options->finalgather_rays      = $3;
                          options->finalgather_maxradius = $4;
                          options->finalgather_minradius = 0.0; }
                | FINALGATHER ACCURACY T_INTEGER floating floating
                        { options->finalgather_view      = miFALSE;
                          options->finalgather_rays      = $3;
                          options->finalgather_maxradius = $4;
                          options->finalgather_minradius = $5; }
                | FINALGATHER ACCURACY VIEW T_INTEGER
                        { options->finalgather_view      = miTRUE;
                          options->finalgather_rays      = $4; }
                | FINALGATHER ACCURACY VIEW T_INTEGER floating
                        { options->finalgather_view      = miTRUE;
                          options->finalgather_rays      = $4;
                          options->finalgather_maxradius = $5;
                          options->finalgather_minradius = 0.0; }
                | FINALGATHER ACCURACY VIEW T_INTEGER floating floating
                        { options->finalgather_view      = miTRUE;
                          options->finalgather_rays      = $4;
                          options->finalgather_maxradius = $5;
                          options->finalgather_minradius = $6; }
                | FINALGATHER FILE_ map_list
                        { mi_api_taglist_reset(&options->finalgather_file,
                                         $3); }
                | FINALGATHER FILTER T_INTEGER
                        { options->finalgather_filter  = $3; }
                | FINALGATHER REBUILD boolean
                        { options->finalgather_rebuild = $3; }
                | FINALGATHER REBUILD FREEZE
                        { options->finalgather_rebuild = 2; }
                | FINALGATHER FALLOFF floating floating
                        { options->fg_falloff_start    = $3;
                          options->fg_falloff_stop     = $4; }
                | FINALGATHER FALLOFF floating
                        { options->fg_falloff_start    = $3;
                          options->fg_falloff_stop     = $3; }
                | FINALGATHER SCALE color
                        { options->finalgather_scale = $3; } 
                | FINALGATHER SECONDARY SCALE color
                        { options->finalgather_sec_scale = $4; } 
                | FINALGATHER PRESAMPLE DENSITY floating 
                        { options->fg_presamp_density = $4; }
                | PHOTONVOL ACCURACY T_INTEGER
                        { options->photonvol_accuracy  = $3; }
                | PHOTONVOL ACCURACY T_INTEGER floating
                        { options->photonvol_accuracy  = $3;
                          options->photonvol_radius    = $4; }
                | PHOTONVOL SCALE color
                        { options->photonvol_scale = $3; }
                | PHOTONMAP FILE_
                        { mi_scene_delete(options->photonmap_file);
                          options->photonmap_file = 0; }
                | PHOTONMAP FILE_ OFF
                        { mi_scene_delete(options->photonmap_file);
                          options->photonmap_file = 0; }
                | PHOTONMAP FILE_ T_STRING
                        { mi_scene_delete(options->photonmap_file);
                          if (($3)[0]) {
                              strcpy((char *)mi_scene_create(
                                            &options->photonmap_file,
                                            miSCENE_STRING, strlen($3)+1), $3);
                              mi_scene_edit_end(options->photonmap_file);
                          } else {
                              options->photonmap_file = 0;
                          }
                          mi_api_release($3);
                        }
                | PHOTONMAP ONLY
                        { options->photonmap_only = miTRUE; }
                | PHOTONMAP ONLY boolean
                        { options->photonmap_only = $3; }
                | PHOTONMAP REBUILD boolean
                        { options->photonmap_rebuild = $3; }
                | APPROXIMATE opt_displace
                | FRAME BUFFER T_INTEGER opt_symbol
                        { mi_api_framebuffer(options, $3, $4); }
                | LUMINANCE WEIGHT NTSC
                        { options->luminance_weight.r = 0.299;
                          options->luminance_weight.g = 0.587;
                          options->luminance_weight.b = 0.114;
                          options->luminance_weight.a = 0.0; }
                | LUMINANCE WEIGHT color
                        { options->luminance_weight = $3; }
                | MAX_ DISPLACE floating
                        { options->maxdisplace = $3; }
                ;

map_list        : '['
                        { taglist = mi_api_dlist_create(miDLIST_TAG); }
                  map_list_items ']'
                        { $$ = taglist; }
                | T_STRING
                        { if (($1)[0]) {
                                taglist = mi_api_dlist_create(miDLIST_TAG);
                                strcpy((char *)mi_scene_create(
                                      &tag, miSCENE_STRING, strlen($1)+1), $1);
                                mi_scene_edit_end(tag);
                                mi_api_release($1);
                                mi_api_dlist_add(taglist, (void *)(miIntptr)tag);
                                $$ = taglist;
                            } else {
                                mi_api_release($1);
                                $$ = NULL;
                            } 
                          }
                | OFF
                        { $$ = NULL; }
                |
                        { $$ = NULL; }
                ;

map_list_items  : T_STRING
                        { strcpy((char *)mi_scene_create(
                                &tag, miSCENE_STRING, strlen($1)+1), $1);
                          mi_scene_edit_end(tag);
                          mi_api_release($1);
                          mi_api_dlist_add(taglist, (void *)(miIntptr)tag); }
                  map_list_next
                ;

map_list_next   :
                | ','
                | ',' map_list_items
                ;

                                                          /* smallparser_end */
filter_type     : BOX
                        { $$ = 'b'; }
                | TRIANGLE
                        { $$ = 't'; }
                | GAUSS
                        { $$ = 'g'; }
                | MITCHELL
                        { $$ = 'm'; }
                | LANCZOS
                        { $$ = 'l'; }
                | CLIP MITCHELL
                        { $$ = 'M'; }
                | CLIP LANCZOS
                        { $$ = 'c'; }
                ;
                                                        /* smallparser_begin */

c_filter_type   : BOX
                        { $$ = 'b'; }
                | CONE
                        { $$ = 'c'; }
                | GAUSS
                        { $$ = 'g'; }
                ;

opt_displace    :       { miAPPROX_DEFAULT(approx); }
                  s_approx_tech ALL
                        { memcpy(&options->approx, &approx, sizeof(miApprox));}
                |       { miAPPROX_DEFAULT(approx); }
                  DISPLACE s_approx_tech ALL
                        { memcpy(&options->approx_displace, &approx,
                                                           sizeof(miApprox)); }
                ;

string_option_item
                : T_STRING boolean
                        { string_options->set($1, $2 != 0); 
                          mi_api_release($1); }
                | T_STRING T_STRING
                        { string_options->set($1, $2);
                          mi_api_release($1);
                          mi_api_release($2); }
                | T_STRING T_INTEGER
                        { string_options->set($1, $2);
                          mi_api_release($1); }
                | T_STRING T_FLOAT
                        { string_options->set($1, (float)$2);
                          mi_api_release($1); }
                | T_STRING floating floating floating
                        { string_options->set($1, (float)$2, (float)$3, (float)$4); 
                          mi_api_release($1); }
                | T_STRING floating floating floating floating
                        { string_options->set($1, (float)$2, (float)$3, (float)$4, (float)$5);
                          mi_api_release($1); }
                ;
                

/*-----------------------------------------------------------------------------
 * camera
 *---------------------------------------------------------------------------*/

camera          : CAMERA symbol
                    {
                        camera = mi_api_camera_begin($2);
                        have_l = have_v = have_e = have_p = 0;
                        if (is_incremental == miFALSE)
                            mi_api_function_delete(&camera->output);
                    }
                  camera_list END CAMERA
                        { mi_api_camera_end(); }
                ;

camera_list     :
                | camera_list camera_item
                ;

camera_item     : camview_item
                | frame_number
                | FIELD T_INTEGER
                        { camera->frame_field = $2; }
                | dummy_attribute       
                ;

camview_item    : OUTPUT
                    {
                        Edit_fb fb(camera->buffertag);
                        fb->reset();
                        mi_api_function_delete(&camera->output);
                    }
                | OUTPUT colorspace_set T_STRING T_STRING 
                    {
                        mi_api_output_colorprofile($2);
                        mi_api_framebuffer_add(camera->buffertag, 0, $3, 0, $4);
                    }
                | OUTPUT colorspace_set T_STRING out_parms T_STRING 
                    {
                        mi_api_output_colorprofile($2);
                        mi_api_framebuffer_add(camera->buffertag, 0, $3, $4, $5);
                    }
                | OUTPUT colorspace_set T_STRING T_STRING T_STRING 
                    {
                        mi_api_output_colorprofile($2);
                        mi_api_framebuffer_add(camera->buffertag, $3, $4, 0, $5);
                    }
                | OUTPUT colorspace_set T_STRING T_STRING out_parms T_STRING 
                    {
                        mi_api_output_colorprofile($2);
                        mi_api_framebuffer_add(camera->buffertag, $3, $4, $5, $6);
                    }
                | OUTPUT colorspace_set function
                    {
                        mi_api_output_colorprofile($2);
                        camera->output = mi_api_function_append(
                            camera->output, mi_api_output_function_def(0, 0, $3));
                    }
                | OUTPUT colorspace_set T_STRING function
                    {
                        mi_api_output_colorprofile($2);
                        mi_api_output_type_identify(&tbm, &ibm, $3);
                        camera->output = mi_api_function_append(
                            camera->output, mi_api_output_function_def(tbm, ibm, $4));
                    }
                | PASS NULL_
                        { mi_api_function_delete(&camera->pass); }
                | PASS pass_samples opt_string WRITE T_STRING
                        { if (!have_p++)
                                mi_api_function_delete(&camera->pass);
                          mi_api_output_type_identify(&tbm, &ibm, $3);
                          camera->pass = mi_api_function_append(camera->pass,
                                mi_api_pass_save_def(tbm, ibm, $2, $5)); }
                | PASS PREP pass_samples opt_string
                  READ T_STRING WRITE T_STRING function_list
                        { if (!have_p++)
                                mi_api_function_delete(&camera->pass);
                          mi_api_output_type_identify(&tbm, &ibm, $4);
                          camera->pass = mi_api_function_append(camera->pass,
                                mi_api_pass_prep_def(tbm, ibm, $3, $6,$8,$9));}
                | PASS MERGE pass_samples opt_string
                  READ string_list opt_function_list
                        { if (!have_p++)
                                mi_api_function_delete(&camera->pass);
                          mi_api_output_type_identify(&tbm, &ibm, $4);
                          camera->pass = mi_api_function_append(camera->pass,
                                mi_api_pass_merge_def(tbm, ibm, $3, $6,0,$7));}
                | PASS MERGE pass_samples opt_string
                  READ string_list WRITE T_STRING opt_function_list
                        { if (!have_p++)
                                mi_api_function_delete(&camera->pass);
                          mi_api_output_type_identify(&tbm, &ibm, $4);
                          camera->pass = mi_api_function_append(camera->pass,
                                mi_api_pass_merge_def(tbm,ibm, $3, $6,$8,$9));}
                | PASS DELETE_ T_STRING
                        { if (!have_p++)
                                mi_api_function_delete(&camera->pass);
                          camera->pass = mi_api_function_append(camera->pass,
                                mi_api_pass_delete_def($3)); }
                | PASS MASK boolean
                        { camera->pass_mask = $3; }
                | VOLUME
                        { mi_api_function_delete(&camera->volume); }
                | VOLUME
                        { if (!have_v++)
                                mi_api_function_delete(&camera->volume); }
                  function_list 
                        { camera->volume = mi_api_function_append(
                                                camera->volume, $3); }
                | ENVIRONMENT
                        { mi_api_function_delete(&camera->environment); }
                | ENVIRONMENT
                        { if (!have_e++)
                                mi_api_function_delete(&camera->environment); }
                  function_list
                        { camera->environment = mi_api_function_append(
                                                camera->environment, $3); }
                | LENS
                        { mi_api_function_delete(&camera->lens); }
                | LENS
                        { if (!have_l++)
                                mi_api_function_delete(&camera->lens); }
                  function_list 
                        { camera->lens = mi_api_function_append(
                                                        camera->lens, $3); }
                | FOCAL floating
                        { camera->focal = $2;
                          camera->orthographic = miFALSE; }
                | FOCAL INFINITY_
                        { camera->focal = 1;
                          camera->orthographic = miTRUE; }
                | APERTURE floating
                        { camera->aperture = $2; }
                | ASPECT floating
                        { camera->aspect = $2; }
                | RESOLUTION T_INTEGER T_INTEGER
                        { camera->x_resolution = $2;
                          camera->y_resolution = $3; }
                | OFFSET floating floating
                        { camera->x_offset = $2;
                          camera->y_offset = $3; }
                | WINDOW T_INTEGER T_INTEGER T_INTEGER T_INTEGER
                        { camera->window.xl = $2;
                          camera->window.yl = $3;
                          camera->window.xh = $4;
                          camera->window.yh = $5; }
                | CLIP floating floating
                        { camera->clip.min = $2;
                          camera->clip.max = $3; }
                | DOF floating floating
                        { camera->focus  = $2;
                          camera->radius = $3; }
                | FRAMEBUFFER T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          if (ctx->buffer_name)
                              mi_api_release(ctx->buffer_name);
                          ctx->buffer_name = $2;
                        }
                        buffer_list
                |       { curr_datatag = &camera->userdata; }
                  data
                ;

out_parms       : QUALITY T_INTEGER
                        { memset($$, 0, 8 * sizeof(float));
                          $$[0] = (float)$2; }
                | EVEN
                        { memset($$, 0, 8 * sizeof(float));
                          $$[1] = 1.0; }
                | ODD
                        { memset($$, 0, 8 * sizeof(float));
                          $$[1] = 2.0; }
                | DOD
                        { memset($$, 0, 8 * sizeof(float));
                          $$[4] = 1.0; }
                | DPI floating
                        { memset($$, 0, 8 * sizeof(float));
                          $$[6] = $2; }
                | COMPRESS T_STRING
                        { memset($$, 0, 8 * sizeof(float));
                          if (!strcmp($2, "none"))
                                $$[0] = 1.0;
                          else if (!strcmp($2, "piz"))
                                $$[0] = 2.0;
                          else if (!strcmp($2, "zip"))
                                $$[0] = 3.0;
                          else if (!strcmp($2, "rle"))
                                $$[0] = 4.0;
                          else if (!strcmp($2, "pxr24"))
                                $$[0] = 5.0;
                          else {
                                mi_api_error("%s is not a valid compression "
                                             "type, using rle compression", $2);
                                $$[0] = 4.0;
                          }
                        }
                ;

frame_number    : FRAME T_INTEGER
                        { camera->frame       = $2;
                          camera->frame_time  = 0;
                          camera->frame_field = 0; }
                | FRAME T_INTEGER floating
                        { camera->frame       = $2;
                          camera->frame_time  = $3;
                          camera->frame_field = 0; }
                ;

                                                        /* smallparser_end */
colorspace_set  : 
                        { $$ = 0; }
                | COLORPROFILE symbol 
                        { $$ = $2; }
                ;
                                                        /* smallparser_begin */
pass_samples    :
                        { $$ = ~0; }
                | SAMPLES T_INTEGER
                        { $$ = $2; }
                ;

string_list     :
                        { $$ = stringlist
                             = mi_api_dlist_create(miDLIST_POINTER); }
                  '[' strings ']'
                ;

strings         : T_STRING
                        { mi_api_dlist_add(stringlist, $1); }
                | strings ',' T_STRING 
                        { mi_api_dlist_add(stringlist, $3); }
                ;


buffer_list     :
                | buffer_list buffer_item
                ;


buffer_item     : DATATYPE T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "datatype", $2);
                          mi_api_release($2);
                        }
                | FILENAME T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "filename", $2);
                          mi_api_release($2);
                        }
                | FILETYPE T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "filetype", $2);
                          mi_api_release($2);
                        }
                | FILTERING boolean
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "filtering", $2 == miTRUE);
                        }
                | COLORPROFILE T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "colorprofile", $2);
                          mi_api_release($2);
                        }
                | COMPRESSION T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "compression", $2);
                          mi_api_release($2);
                        }
                | FIELD T_STRING
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "field", $2);
                          mi_api_release($2);
                        }
                | QUALITY T_INTEGER
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "quality", (int)$2);
                        }
                | DOD boolean
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "dod", $2 == miTRUE);
                        }
                | DPI T_INTEGER
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "dpi", $2);
                        }
                | PRIMARY boolean
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "primary", $2 == miTRUE);
                        }
                | USEOPACITY boolean
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "useopacity", $2 == miTRUE);
                        }
                | USEPRIMARY boolean
                        {
                          Edit_fb fb(camera->buffertag);
                          fb->set(ctx->buffer_name, "useprimary", $2 == miTRUE);
                        }
                ;
                                                          /* smallparser_end */


/*-----------------------------------------------------------------------------
 * instance
 *---------------------------------------------------------------------------*/

instance        : INSTANCE symbol
                        { curr_inst = mi_api_instance_begin($2);
                          if (!curr_inst) {
                                  memset(&dummy_inst, 0, sizeof(dummy_inst));
                                  curr_inst = &dummy_inst;
                          }
                          override = miFALSE; }
                  inst_item inst_func
                  inst_flags
                  inst_params
                        { mi_api_instance_end($4, $5, $7); }
                  END INSTANCE
                ;

inst_item       :
                        { $$ = 0; }
                | symbol
                        { $$ = $1; }
                ;

inst_func       :
                        { $$ = miNULLTAG; }
                | GEOMETRY function_list
                        { $$ = $2; }
                ;

inst_flags      :
                | inst_flag inst_flags
                ;

inst_flag       : VISIBLE boolean
                        { curr_inst->visible    = $2 ? 2 : 1; }
                | SHADOW boolean
                        { curr_inst->shadow     = $2 ? 0x03 : 0x06; }
                | SHADOW T_INTEGER
                        { curr_inst->shadow     = ($2 & 0x0f); }
                | SHADOWMAP boolean
                        { curr_inst->shadowmap  = $2 ? 2 : 1; }
                | TRACE boolean
                        { curr_inst->reflection =
                          curr_inst->refraction = $2 ? 0x03 : 0x0c;
                          curr_inst->finalgather= $2 ? 0x23 : 0x10; }
                | REFLECTION T_INTEGER
                        { curr_inst->reflection = ($2 & 0x0f); }
                | REFRACTION T_INTEGER
                        { curr_inst->refraction = ($2 & 0x0f); }
                | TRANSPARENCY T_INTEGER
                        { curr_inst->transparency = ($2 & 0x0f); }
                | FACE FRONT
                        { curr_inst->face       = 'f'; }
                | FACE BACK
                        { curr_inst->face       = 'b'; }
                | FACE BOTH
                        { curr_inst->face       = 'a'; }
                | SELECT boolean
                        { curr_inst->select     = $2 ? 2 : 1; }
                | CAUSTIC
                        { curr_inst->caustic   &= 0x30;
                          curr_inst->caustic   |= 0x03; }
                | CAUSTIC boolean
                        { curr_inst->caustic   &= 0x0f;
                          curr_inst->caustic   |= $2 ? 0x20 : 0x10; }
                | CAUSTIC T_INTEGER
                        { curr_inst->caustic   &= 0x30;
                          curr_inst->caustic   |= ($2 & 0x0f); }
                | GLOBILLUM
                        { curr_inst->globillum &= 0x30;
                          curr_inst->globillum |= 0x03; }
                | GLOBILLUM boolean
                        { curr_inst->globillum &= 0x0f;
                          curr_inst->globillum |= $2 ? 0x20 : 0x10; }
                | GLOBILLUM T_INTEGER
                        { curr_inst->globillum &= 0x30;
                          curr_inst->globillum |= ($2 & 0x0f); }
                | FINALGATHER
                        { curr_inst->finalgather &= 0x30;
                          curr_inst->finalgather |= 0x03; }
                | FINALGATHER boolean
                        { curr_inst->finalgather &= 0x0f;
                          curr_inst->finalgather |= $2 ? 0x20 : 0x10; }
                | FINALGATHER T_INTEGER
                        { curr_inst->finalgather &= 0x30;
                          curr_inst->finalgather |= ($2 & 0x0f); }
                                                        /* hardware_begin */
                | SHADING SAMPLES floating
                        { curr_inst->shading_samples = $3; }
                | HARDWARE
                        { curr_inst->hardware   = 2; }
                | HARDWARE boolean
                        { curr_inst->hardware   = $2 ? 2 : 1; }
                                                        /* hardware_end */
                | HIDE boolean
                        { curr_inst->off = $2; }
                | TRANSFORM
                        { curr_inst->tf.function = miNULLTAG;
                          mi_matrix_ident(curr_inst->tf.global_to_local); }
                | TRANSFORM function
                        { curr_inst->tf.function = $2;
                          mi_matrix_ident(curr_inst->tf.global_to_local); }
                | transform
                        { curr_inst->tf.function = miNULLTAG;
                          mi_matrix_copy(
                                curr_inst->tf.global_to_local, $1);
                          if (!mi_matrix_invert(curr_inst->tf.local_to_global,
                                               curr_inst->tf.global_to_local)){
                                mi_api_warning("singular matrix, using "
                                                                "identity");
                                mi_matrix_ident(curr_inst->tf.global_to_local);
                                mi_matrix_ident(curr_inst->tf.local_to_global);
                        }}
                | MOTION OFF
                        { mi_matrix_null(curr_inst->motion_transform);
                          curr_inst->gen_motion = miGM_OFF; }
                | MOTION TRANSFORM
                        { mi_matrix_null(curr_inst->motion_transform);
                          curr_inst->gen_motion = miGM_INHERIT; }
                | MOTION transform
                        { mi_matrix_copy(curr_inst->motion_transform, $2);
                          curr_inst->gen_motion = miGM_TRANSFORM; }
                | LIGHT incl_excl light_list 
                        { curr_inst->exclusive   = $2;   
                          curr_inst->light_list = $3; }
                | LIGHT SHADOW incl_excl light_list
                        { curr_inst->shadow_excl = $3;
                          curr_inst->shadow_list = $4; } 
                | MATERIAL
                        { curr_inst->material       = miNULLTAG;
                          curr_inst->mtl_array_size = 0;
                          curr_inst->mtl_override   = miFALSE; }
                  inst_mtl
                | TAG T_INTEGER
                        { curr_inst->label = $2; }
                |       { curr_datatag = &curr_inst->userdata; }
                  data
                | OVERRIDE
                        { override = miTRUE; }  /* for approx and material */
                                                        /* smallparser_begin */
                | APPROXIMATE
                        { mi_api_instance_approx(0, miFALSE); }
                | APPROXIMATE
                        { miAPPROX_DEFAULT(approx);
                          curr_inst->approx_override = override;
                          override = miFALSE; }
                  '[' inst_approx_arr ']'
                | dummy_attribute  
                                                          /* smallparser_end */
                ;

inst_params     :
                        { $$ = (miTag)-1; }
                | '(' ')'
                        { $$ = miNULLTAG; }
                | '('
                        { if (!ctx->inheritance_func)
                            mi_api_error("no inheritance function in options");
                          else
                            mi_api_function_call(mi_api_strdup(
                                                 ctx->inheritance_func)); }
                  parameter_seq comma_rparen
                        { $$ = mi_api_function_call_end(0); }
                ;

comma_rparen    : ')'
                | ',' ')'
                ;

inst_mtl        :
                | symbol
                        { curr_inst->material     = mi_api_material_lookup($1);
                          curr_inst->mtl_override = override;
                          override = miFALSE; }
                | '['
                        { taglist = mi_api_dlist_create(miDLIST_TAG); }
                  inst_mtl_array ']'
                        { curr_inst->mtl_array_size = taglist->nb;
                          curr_inst->material       = mi_api_taglist(taglist);
                          curr_inst->mtl_override   = override; }
                ;

inst_mtl_array  : symbol
                        { mi_api_dlist_add(taglist,
                                (void *)(miIntptr)mi_api_material_lookup($1));}
                  inst_mtl_next
                ;

inst_mtl_next   :
                | ','
                | ',' inst_mtl_array
                ;

                                                        /* smallparser_begin */
inst_approx_arr : approx_flags APPROXIMATE s_approx_tech ALL
                        { mi_api_instance_approx(&approx, miFALSE);
                          miAPPROX_DEFAULT(approx); }
                  inst_approx_nxt
                | approx_flags APPROXIMATE DISPLACE s_approx_tech ALL
                        { mi_api_instance_approx(&approx, miTRUE);
                          miAPPROX_DEFAULT(approx); }
                  inst_approx_nxt
                ;

inst_approx_nxt :
                | ','
                | ',' inst_approx_arr
                ;

                                                          /* smallparser_end */
incl_excl       : 
                    { $$ = 0 ; /* not exclusive */ }
                | T_STRING
                    { if(!strcmp($1, "exclusive")) {
                           $$ = 1;
                      } else {
                           $$ = 0;
                           mi_api_nwarning(127,"instance light list modifier \"%s\"" 
                            " is not \"exclusive\" -- using non-exclusive light list!", $1);
                      }
                      mi_mem_release($1);
                    }
                ; 
                
light_list      : '[' 
                    { mi_api_light_list_begin(); }
                  light_list_element ']'
                    { $$ = mi_api_light_list_end(); }
                | '[' ']'
                    { mi_api_light_list_begin();
                      $$ = mi_api_light_list_end(); }
                ;
                

light_list_element : symbol
                    { mi_api_light_list_add($1); } 
                 | light_list_element light_list_next symbol
                    { mi_api_light_list_add($3); }
                ;
                
light_list_next : 
                | ','
                ; 

/*-----------------------------------------------------------------------------
 * instgroup
 *---------------------------------------------------------------------------*/

instgroup       : INSTGROUP symbol
                        { curr_group = mi_api_instgroup_begin($2);
                          mi_api_instgroup_clear(); }
                  group_flags
                  group_kids END INSTGROUP
                        { mi_api_instgroup_end(); }
                ;

group_flags     :
                | group_flag group_flags
                ;

group_flag      : MERGE floating
                        { curr_group->merge = $2;
                          curr_group->merge_group = $2 >= miMERGE_MIN; }
                | TAG T_INTEGER
                        { curr_group->label = $2; }
                |       { curr_datatag = &curr_group->userdata; }
                  data
                | dummy_attribute         
                ;

group_kids      :
                | group_kids
                  symbol
                        { mi_api_instgroup_additem($2); }
                ;

/*-----------------------------------------------------------------------------
 * assembly
 *---------------------------------------------------------------------------*/

assembly        : ASSEMBLY symbol
                        { curr_assembly = mi_api_assembly_begin($2); }
                | assembly_flags END ASSEMBLY
                        { mi_api_assembly_end(); }
                ;

assembly_flags  : assembly_flag assembly_flags
                | assembly_flag
                ;

assembly_flag   : BOX vector vector
                        { curr_assembly->bbox_min = $2;
                          curr_assembly->bbox_max = $3; }
                | BOX
                        { curr_assembly->bbox_min = nullvec;
                          curr_assembly->bbox_max = nullvec; }
                | MOTION BOX vector vector
                        { curr_assembly->bbox_min_m = $3;
                          curr_assembly->bbox_max_m = $4; }
                | MOTION BOX
                        { curr_assembly->bbox_min_m = nullvec;
                          curr_assembly->bbox_max_m = nullvec; }
                | FILE_ T_STRING
                        { mi_api_assembly_filename($2); }
                ;

/*****************************************************************************
 *************************    either    **************************************
 *****************************************************************************/

/*-----------------------------------------------------------------------------
 * function declaration
 *---------------------------------------------------------------------------*/

function_decl   : shret_type_nosh T_STRING parm_decl_list
                        { mi_api_funcdecl_begin($1, $2, $3);
                          mi_api_funcdecl_end(); }
                | SHADER shret_type T_STRING parm_decl_list
                        { if (!(curr_decl = mi_api_funcdecl_begin($2,$3,$4))){
                                memset(&dummy_decl, 0, sizeof(dummy_decl));
                                curr_decl = &dummy_decl;
                          } }
                  declare_req_seq END DECLARE
                        { mi_api_funcdecl_end(); }
                ;

shret_type      : shret_type_nosh
                        { $$ = $1; }
                | SHADER
                        { $$ = mi_api_parameter_decl(miTYPE_SHADER, 0, 0); }
                ;

shret_type_nosh :
                        { $$ = mi_api_parameter_decl(miTYPE_COLOR, 0, 0); }
                | simple_type
                        { $$ = mi_api_parameter_decl((miParam_type)$1, 0, 0); }
                | STRUCT '{' shret_decl_seq '}'
                        { miParameter *parm =
                                mi_api_parameter_decl(miTYPE_STRUCT, 0, 0);
                          mi_api_parameter_child(parm, $3);
                          $$ = parm; }
                ;

shret_decl_seq  : shret_decl_seq ',' shret_decl
                        { $$ = mi_api_parameter_append($1, $3); }
                | shret_decl
                        { $$ = $1; }
                ;

shret_decl      : simple_type symbol
                        { $$ = mi_api_parameter_decl((miParam_type)$1, $2, 0); }
                | SHADER symbol
                        { $$ = mi_api_parameter_decl(miTYPE_SHADER, $2, 0); }
                | DATA symbol
                        { $$ = mi_api_parameter_decl(miTYPE_DATA,   $2, 0); }
                ;

parm_decl_list  : '(' parm_decl_seq ')'
                        { $$ = $2; }
                | '(' parm_decl_seq ',' ')'
                        { $$ = $2; }
                | '(' ')'
                        { $$ = 0; }
                ;

parm_decl_seq   : parm_decl_seq ',' parm_decl
                        { $$ = mi_api_parameter_append($1, $3); }
                | parm_decl
                        { $$ = $1; }
                ;

parm_decl       : decl_simple decl_default
                        { $$ = $1; }
                | SHADER symbol
                        { $$ = mi_api_parameter_decl(miTYPE_SHADER, $2, 0); }
                | DATA symbol
                        { $$ = mi_api_parameter_decl(miTYPE_DATA,   $2, 0); }
                | STRUCT symbol '{' parm_decl_seq '}'
                        { miParameter *parm =
                                mi_api_parameter_decl(miTYPE_STRUCT, $2, 0);
                          mi_api_parameter_child(parm, $4);
                          $$ = parm; }
                | ARRAY parm_decl
                        { miParameter *parm =
                                mi_api_parameter_decl(miTYPE_ARRAY, 0, 0);
                          mi_api_parameter_child(parm, $2);
                          $$ = parm; }
                ;

decl_simple     : simple_type symbol
                        { $$ = mi_api_parameter_decl((miParam_type) $1, $2, 0); }
                ;

simple_type     : BOOLEAN
                        { $$ = miTYPE_BOOLEAN; }
                | INTEGER
                        { $$ = miTYPE_INTEGER; }
                | SCALAR
                        { $$ = miTYPE_SCALAR; }
                | STRING
                        { $$ = miTYPE_STRING; }
                | COLOR
                        { $$ = miTYPE_COLOR; }
                | VECTOR
                        { $$ = miTYPE_VECTOR; }
                | TRANSFORM
                        { $$ = miTYPE_TRANSFORM; }
                | SCALAR TEXTURE
                        { $$ = miTYPE_SCALAR_TEX; }
                | VECTOR TEXTURE
                        { $$ = miTYPE_VECTOR_TEX; }
                | COLOR TEXTURE
                        { $$ = miTYPE_COLOR_TEX; }
                | LIGHTPROFILE
                        { $$ = miTYPE_LIGHTPROFILE; }
                | SPECTRUM
                        { $$ = miTYPE_SPECTRUM; }
                | LIGHT
                        { $$ = miTYPE_LIGHT; }
                | MATERIAL
                        { $$ = miTYPE_MATERIAL; }
                | GEOMETRY
                        { $$ = miTYPE_GEOMETRY; }
                ;

decl_default    :
                | DEFAULT decl_def_values
                ;

decl_def_values :
                | decl_def_value decl_def_values
                ;

decl_def_value  : boolean
                        { int value = $1;
                          mi_api_parameter_default(miTYPE_BOOLEAN, &value); }
                | T_INTEGER
                        { int value = $1;
                          mi_api_parameter_default(miTYPE_INTEGER, &value); }
                | T_FLOAT
                        { float value = $1;
                          mi_api_parameter_default(miTYPE_SCALAR,  &value); }
                ;

declare_req_seq :
                | declare_req declare_req_seq
                ;

declare_req     : gui
                | SCANLINE OFF
                        { curr_decl->phen.scanline = 1; }
                | SCANLINE ON
                        { curr_decl->phen.scanline = 2; }
                | TRACE OFF
                        { curr_decl->phen.trace = 1; }
                | TRACE ON
                        { curr_decl->phen.trace = 2; }
                | SHADOW OFF
                        { curr_decl->phen.shadow = 1; }
                | SHADOW ON
                        { curr_decl->phen.shadow = 2; }
                | SHADOW SORT
                        { curr_decl->phen.shadow = 'l'; }
                | SHADOW SEGMENTS
                        { curr_decl->phen.shadow = 's'; }
                | FACE FRONT
                        { curr_decl->phen.face = 'f'; }
                | FACE BACK
                        { curr_decl->phen.face = 'b'; }
                | FACE BOTH
                        { curr_decl->phen.face = 'a'; }
                | TEXTURE T_INTEGER
                        { curr_decl->phen.mintextures = $2; }
                | BUMP T_INTEGER
                        { curr_decl->phen.minbumps = $2; }
                | DERIVATIVE
                        { curr_decl->phen.deriv1 =
                          curr_decl->phen.deriv2 = 0; }
                | DERIVATIVE T_INTEGER
                        { if ($2 == 1)
                                curr_decl->phen.deriv1 = miTRUE;
                          else if ($2 == 2)
                                curr_decl->phen.deriv2 = miTRUE;
                          else
                                mi_api_error("derivative not 1 or 2"); }
                | DERIVATIVE T_INTEGER T_INTEGER
                        { if ($2 == 1 || $3 == 1)
                                curr_decl->phen.deriv1 = miTRUE;
                          else if ($2 == 2 || $3 == 2)
                                curr_decl->phen.deriv2 = miTRUE;
                          if ($2 != 1 && $2 != 2 || $3 != 1 && $3 != 2)
                                mi_api_error("derivative not 1 or 2"); }
                | OBJECT SPACE
                        { curr_decl->phen.render_space = 'o'; }
                | CAMERA SPACE
                        { curr_decl->phen.render_space = 'c'; }
                | MIXED SPACE
                        { curr_decl->phen.render_space = 'm'; }
                | WORLD SPACE
                        { mi_api_warning("world space statement ignored"); }
                | PARALLEL_
                        { curr_decl->phen.parallel = miTRUE; }
                | VOLUME LEVEL T_INTEGER
                        { curr_decl->phen.volume_level = $3; }
                | VERSION T_INTEGER
                        { curr_decl->version = $2; }
                | APPLY apply_list
                        { curr_decl->apply = $2; }
                                                        /* hardware_begin */
                | HARDWARE
                        { curr_hw = mi_api_hardware_begin(); }
                  hardware_list
                        { curr_decl->hardware = mi_api_hardware_end(curr_hw); }
                                                        /* hardware_end */
                ;
                                                        /* hardware_begin */
hardware_list   :
                | '(' hardware_seq ')'
                | '(' hardware_seq ',' ')'
                ;

hardware_seq    :
                | hardware_seq ',' hardware_attr
                | hardware_attr
                ;

hardware_attr   : UNIFORM  T_STRING
                        { mi_api_hardware_attr(curr_hw, 'u', $2); }
                | VERTEX   T_STRING
                        { mi_api_hardware_attr(curr_hw, 'v', $2); }
                | FRAGMENT T_STRING
                        { mi_api_hardware_attr(curr_hw, 'f', $2); }
                ;
                                                        /* hardware_end */

apply_list      : apply                 { $$ = $1; }
                | apply_list  ',' apply { $$ = $1 | $3; }
                ;

apply           : LENS                  { $$ = miAPPLY_LENS;            }
                | MATERIAL              { $$ = miAPPLY_MATERIAL;        }
                | LIGHT                 { $$ = miAPPLY_LIGHT;           }
                | SHADOW                { $$ = miAPPLY_SHADOW;          }
                | ENVIRONMENT           { $$ = miAPPLY_ENVIRONMENT;     }
                | VOLUME                { $$ = miAPPLY_VOLUME;          }
                | TEXTURE               { $$ = miAPPLY_TEXTURE;         }
                | PHOTON                { $$ = miAPPLY_PHOTON;          }
                | GEOMETRY              { $$ = miAPPLY_GEOMETRY;        }
                | DISPLACE              { $$ = miAPPLY_DISPLACE;        }
                | EMITTER               { $$ = miAPPLY_PHOTON_EMITTER;  }
                | OUTPUT                { $$ = miAPPLY_OUTPUT;          }
                | LIGHTMAP              { $$ = miAPPLY_LIGHTMAP;        }
                | PHOTONVOL             { $$ = miAPPLY_PHOTONVOL;       }
                | STATE                 { $$ = miAPPLY_STATE;           }
                ;


/*-----------------------------------------------------------------------------
 * function instance
 *---------------------------------------------------------------------------*/

                                                        /* smallparser_begin */
opt_function_list:
                        { $$ = 0; }
                | function_list
                        { $$ = $1; }
                ;
                                                          /* smallparser_end */

function_list   :
                        { funclist = miNULLTAG; }
                  func_list
                        { $$ = funclist; }
                ;

func_list       : function
                        { funclist = $1; }
                | func_list function
                        { funclist = mi_api_function_append(funclist, $2); }
                ;

function_array  : '[' ']'
                        { $$ = miNULLTAG; }
                | '['
                        { funclist = miNULLTAG; }
                  func_array ']'
                        { $$ = funclist; }
                ;

func_array      : function
                        { funclist = $1; }
                | func_array ',' function
                        { funclist = mi_api_function_append(funclist, $3); }
                ;

function        : T_STRING
                        { mi_api_function_call($1); }
                  parameter_list
                        { $$ = mi_api_function_call_end(functag); functag = 0;}
                | '=' symbol
                        { $$ = mi_api_function_assign($2); }
                | '=' opt_incremental SHADER symbol function
                        { mi_api_shader_add($4, $5); $$ = $5;
                          mi_api_incremental(is_incremental);
                          mi_api_private(session_depth); }
                ;

opt_incremental :
                        { mi_api_incremental(miFALSE); }
                | INCREMENTAL
                        { mi_api_incremental(miTRUE); }
                ;

parameter_list  : '(' ')'
                | '(' parameter_seq ')'
                | '(' parameter_seq ',' ')'
                ;

parameter_seq   : parameter
                | parameter_seq ',' parameter
                ;

parameter       : symbol
                        { mi_api_parameter_name($1); }
                  colorspace_set value_list
                        { mi_api_parameter_colorprofile($3); }
                ;

value_list      : value
                | value_list value
                ;

value           : NULL_
                | boolean
                        { int value = $1;
                          mi_api_parameter_value(miTYPE_BOOLEAN, &value,0,0); }
                | T_INTEGER
                        { int value = $1;
                          mi_api_parameter_value(miTYPE_INTEGER, &value,0,0); }
                | T_FLOAT
                        { float value = $1;
                          mi_api_parameter_value(miTYPE_SCALAR,  &value,0,0); }
                | symbol
                        { mi_api_parameter_value(miTYPE_STRING,  $1, 0, 0); }
                | '=' symbol
                        { mi_api_parameter_shader($2); }
                | '=' INTERFACE_ symbol
                        { mi_api_parameter_interface($3); }
                | '{'
                        { mi_api_parameter_push(miFALSE); }
                  parameter_seq '}'
                        { mi_api_parameter_pop(); }
                | '['
                        { mi_api_parameter_push(miTRUE); }
                  array_value_seq ']'
                        { mi_api_parameter_pop(); }
                | '[' ']'
                        { mi_api_parameter_push(miTRUE);
                          mi_api_parameter_pop(); }
                ;

array_value_seq :       { mi_api_new_array_element(); }
                  value_list
                  array_value_cont
                ;

array_value_cont:
                | ','
                        { mi_api_new_array_element(); }
                  value_list array_value_cont
                ;


/*-----------------------------------------------------------------------------
 * user data
 *---------------------------------------------------------------------------*/

userdata        : DATA symbol data_label T_INTEGER
                        { curr_data = mi_api_data_begin($2, 0,
                                                        (void *)(miIntptr)$4);
                          curr_data->label = label; }
                  '[' data_bytes_list ']'
                        { mi_api_data_end(); }
                | DATA symbol data_label symbol
                        { curr_data = mi_api_data_begin($2, 1,
                                                        (void *)(miIntptr)$4);
                          curr_data->label = label;
                          mi_api_data_end(); }
                | DATA symbol data_label symbol '('
                        { mi_api_function_call($4); }
                  parameter_seq comma_rparen
                        { tag = mi_api_function_call_end(0);
                          curr_data = mi_api_data_begin($2, 2,
                                                        (void *)(miIntptr)tag);
                          curr_data->label = label;
                          mi_api_data_end(); }
                ;

data_label      :
                        { label = 0; }
                | TAG T_INTEGER
                        { label = $2; }
                ;

data_bytes_list :
                | data_bytes_list T_BYTE_STRING
                        { mi_api_data_byte_copy($2.len, $2.bytes); }
                ;

data_decl       : DATA T_STRING parm_decl_list
                        { if (curr_decl = mi_api_funcdecl_begin(0, $2, $3))
                                curr_decl->type = miFUNCTION_DATA; }
                  data_decl_req END DECLARE
                        { if (curr_decl) mi_api_funcdecl_end(); }
                ;

data_decl_req   :
                | gui
                | VERSION T_INTEGER
                        { if (curr_decl) curr_decl->version = $2; }
                | APPLY apply_list
                        { if (curr_decl) curr_decl->apply = $2; }
                ;

data            : DATA symbol
                        { *curr_datatag = mi_api_data_append(*curr_datatag,
                                                mi_api_data_lookup($2)); }
                | DATA NULL_
                        { *curr_datatag = 0; }
                ;


/*-----------------------------------------------------------------------------
 * phenomenon declaration
 *---------------------------------------------------------------------------*/

phenomenon_decl : PHENOMENON shret_type T_STRING parm_decl_list
                        { curr_decl = mi_api_phen_begin($2, $3, $4);
                          if (!curr_decl) {
                                  memset(&dummy_decl, 0, sizeof(dummy_decl));
                                  curr_decl = &dummy_decl;
                          } }
                  phen_body_list
                  END DECLARE
                        { mi_api_phen_end(); }
                ;

phen_body_list  :
                | phen_body_list phen_body
                ;

phen_body       : SHADER symbol function_list
                        { mi_api_shader_add($2, $3); }
                | material
                | light
                | instance
                | declare_req
                | ROOT phen_root
                        { if (curr_decl->phen.root)
                                mi_api_error("multiple roots not allowed");
                          else
                                curr_decl->phen.root = $2; }
                | OUTPUT function
                        { curr_decl->phen.output = mi_api_function_append(
                                curr_decl->phen.output,
                                mi_api_output_function_def(0, 0, $2)); }
                | OUTPUT T_STRING function
                        { mi_api_output_type_identify(&tbm, &ibm, $2);
                          curr_decl->phen.output = mi_api_function_append(
                                curr_decl->phen.output,
                                mi_api_output_function_def(tbm, ibm, $3)); }
                | LENS function_list
                        { curr_decl->phen.lens = mi_api_function_append(
                                                curr_decl->phen.lens, $2); }
                | VOLUME function_list
                        { curr_decl->phen.volume = mi_api_function_append(
                                                curr_decl->phen.volume, $2); }
                | ENVIRONMENT function_list
                        { curr_decl->phen.environment = mi_api_function_append(
                                           curr_decl->phen.environment, $2); }
                | GEOMETRY function_list
                        { curr_decl->phen.geometry = mi_api_function_append(
                                                curr_decl->phen.geometry, $2);}
                | CONTOUR STORE function
                        { curr_decl->phen.contour_store = $3; }
                | CONTOUR CONTRAST function
                        { curr_decl->phen.contour_contrast = $3; }
                | OUTPUT PRIORITY T_INTEGER
                        { curr_decl->phen.output_seqnr = $3; }
                | LENS PRIORITY T_INTEGER
                        { curr_decl->phen.lens_seqnr = $3; }
                | VOLUME PRIORITY T_INTEGER
                        { curr_decl->phen.volume_seqnr = $3; }
                ;

phen_root       : MATERIAL symbol
                        { if (*curr_decl->declaration != 'm') {
                                mi_api_error("not a material phenomenon");
                                $$ = 0;
                          } else
                                $$ = mi_api_material_lookup($2); }
                | LIGHT symbol
                        { if (*curr_decl->declaration != 'l') {
                                mi_api_error("not a light phenomenon");
                                $$ = 0;
                          } else
                                $$ = mi_api_light_lookup($2); }
                | function_list
                        { $$ = 0;
                          if (*curr_decl->declaration == 'm')
                                mi_api_error("must use ``root material''");
                          else if (*curr_decl->declaration == 'l')
                                mi_api_error("must use ``root light''");
                          else
                                $$ = mi_api_function_append(
                                                curr_decl->phen.root, $1); }
                ;


/*-----------------------------------------------------------------------------
 * texture
 *---------------------------------------------------------------------------*/

texture         :       { pyramid_filter = 0.; 
                          curr_cprof = 0; }
                  tex_flags tex_type TEXTURE symbol colorspace_set
                        { functag = mi_api_texture_begin($5, $3, $2);
                          mi_api_texture_set_colorprofile($6);
                          mi_api_texture_set_filter(pyramid_filter); }
                  tex_data
                        { if (pyramid_filter > 0. && functag &&
                              (mi_db_type(functag) != miSCENE_IMAGE)) {
                                mi_api_nwarning(42, "cannot filter shaders");
                          }
                          mi_api_texture_end();
                          functag = 0; }
                ;

tex_flags       :
                        { $$ = 0; }
                | tex_flag tex_flags
                        { $$ = $1 | $2; }
                ;

tex_flag        : LOCAL
                        { $$ = 1; }
                | FILTER
                        { pyramid_filter = 1.; $$ = 2; }
                | FILTER floating
                        { pyramid_filter = $2;
                          $$ = (pyramid_filter > 0.) ? 2 : 0; }
                | WRITABLE
                        { $$ = 4; }
                ;

tex_type        : COLOR
                        { $$ = 0; }
                | SCALAR
                        { $$ = 1; }
                | VECTOR
                        { $$ = 2; }
                ;

tex_data        : '[' T_INTEGER T_INTEGER ']'
                        { mi_api_texture_array_def_begin($2, $3, 1); }
                  tex_bytes_list
                        { functag = mi_api_texture_array_def_end(); }
                | '[' T_INTEGER T_INTEGER T_INTEGER ']'
                        { mi_api_texture_array_def_begin($2, $3, $4); }
                  tex_bytes_list
                        { functag = mi_api_texture_array_def_end(); }
                | tex_func_list
                        { functag = mi_api_texture_function_def($1); }
                | T_STRING
                        { functag = mi_api_texture_file_def($1); }
                | T_STRING '[' T_INTEGER T_INTEGER ']'
                        { mi_api_texture_file_size($3, $4, 1, miIMG_TYPE_ANY);
                          functag = mi_api_texture_file_def($1); }
                | T_STRING '[' T_INTEGER T_INTEGER T_INTEGER ']'
                        { mi_api_texture_file_size($3, $4, $5, miIMG_TYPE_ANY);
                          functag = mi_api_texture_file_def($1); }
                | T_STRING T_STRING '[' T_INTEGER T_INTEGER ']' 
                        { mi_api_texture_file_size($4, $5, 0, 
                                        mi_api_texture_type_identify($2));
                          functag = mi_api_texture_file_def($1); }
                | T_STRING T_STRING T_STRING '[' T_INTEGER T_INTEGER ']'
                        { mi_api_texture_file_size($5, $6, 0,
                                        mi_api_texture_type_identify($2));
                          functag = mi_api_texture_fileext_def($1, $3); }
                          
                                         
                ;

tex_func_list   : function
                        { $$ = $1; }
                | function tex_func_list
                        { $$ = mi_api_function_append($1, $2); }
                ;

tex_bytes_list  :
                | tex_bytes_list T_BYTE_STRING
                        { mi_api_texture_byte_copy($2.len, $2.bytes); }
                ;


/*-----------------------------------------------------------------------------
 * light profiles
 *---------------------------------------------------------------------------*/

profile_data    : LIGHTPROFILE symbol
                        { lprof = mi_api_lightprofile_begin($2); }
                  lprof_ops
                  END LIGHTPROFILE
                        { mi_api_lightprofile_end(); }
                ;

lprof_ops       : lprof_ops lprof_op
                |
                ;

lprof_op        : FORMAT IES
                        { lprof->format = miLP_STD_IES; }
                | FORMAT EULUMDAT
                        { lprof->format = miLP_STD_EULUMDAT; }
                | FLAGS T_INTEGER
                        { lprof->flags = $2; }
                | FILE_ T_STRING
                        { char* fn = (char*) mi_scene_create(&lprof->filename,
                                        miSCENE_STRING, strlen($2)+1);
                          strcpy(fn, $2);
                          mi_api_release($2);
                          mi_scene_edit_end(lprof->filename); }
                | HERMITE T_INTEGER
                        { lprof->base    = miLP_BASIS_HERMITE;
                          lprof->quality = $2; }
                | RESOLUTION T_INTEGER T_INTEGER
                        { lprof->n_horz_angles = $2;
                          lprof->n_vert_angles = $3; }
                ;


/*-----------------------------------------------------------------------------
 * color profiles
 *---------------------------------------------------------------------------*/

cprof           : COLORPROFILE symbol
                        { cprof = mi_api_colorprofile_begin($2); }
                        cprof_ops
                  END COLORPROFILE
                        { mi_api_colorprofile_end(); }
                ;

cprof_ops       : cprof_ops cprof_op
                | 
                ;

cprof_op        : COLOR SPACE T_STRING
                        { cprof->space = mi_api_colorprofile_space($3); }
                | TRANSFORM floating floating floating
                            floating floating floating
                            floating floating floating
                        {
                           if((cprof->space & miCPROF_SPACEMASK )
                                                        == miCPROF_CUSTOM) { 
                                miMatrix mat;
                                cprof->space |= miCPROF_CID_NOT_ENOUGH;
                                mat[0]  = $2;  
                                mat[1]  = $3;   
                                mat[2]  = $4;
                                mat[3]  = 0;

                                mat[4]  = $5;  
                                mat[5]  = $6;   
                                mat[6]  = $7;
                                mat[7]  = 0;
                
                                mat[8]  = $8;  
                                mat[9]  = $9;  
                                mat[10] = $10; 
                                mat[11] = 0;

                                mat[12] = 0;
                                mat[13] = 0;
                                mat[14] = 0;
                                mat[15] = 1;

                                mi_api_colorprofile_custom(cprof, mat);
                           }
                        }
                | SPECTRUM 
                        { cprof->space = miCPROF_SPECTRUM;
                          mi_api_colorprofile_gamma(0.0f, 0.0f, miFALSE);  }
                | WHITE floating floating 
                        { /* white point chroma (x,y), intensity 1 lumen */ 
                          cprof->white_adapt = miTRUE;
                          cprof->white.r = $2/$3;
                          cprof->white.g = 1.0f;
                          cprof->white.b = (1.0f-$2-$3)/$3;
                          mi_colorprofile_ciexyz_to_internal(&cprof->white); }
                | WHITE floating floating floating 
                        { /* CIE XYZ coords of the white point */
                          cprof->white_adapt = miTRUE;
                          cprof->white.r = $2;
                          cprof->white.g = $3; 
                          cprof->white.b = $4; 
                          mi_colorprofile_ciexyz_to_internal(&cprof->white); }
                | WHITE D T_INTEGER
                        { cprof->white_adapt = miTRUE; 
                          mi_api_colorprofile_white(&cprof->white, $3, 1.0f); }
                | WHITE D T_INTEGER floating
                        { cprof->white_adapt = miTRUE;
                          mi_api_colorprofile_white(&cprof->white, $3, $4); }
                | WHITE boolean
                        { cprof->white_adapt = $2; }
                | GAMMA floating 
                        { mi_api_colorprofile_gamma($2, 0, miFALSE); }
                | GAMMA floating floating
                        { mi_api_colorprofile_gamma($2, $3, miFALSE); }
                | GAMMA floating floating boolean
                        { mi_api_colorprofile_gamma($2, $3, $4); }
                ;


/*-----------------------------------------------------------------------------
 * light spectra
 *----------------------------------------------------------------------------*/

spectrum_data   : SPECTRUM symbol
                        { mi_api_spectrum_begin($2); }
                  spectrum_scalars
                  END SPECTRUM
                        { mi_api_spectrum_end(); }
                ;

spectrum_scalars : 
                | spectrum_scalars floating floating
                        {  mi_api_spectrum_pair_add($2, $3); }
                ;

/*-----------------------------------------------------------------------------
 * light
 *---------------------------------------------------------------------------*/

light           : LIGHT symbol
                        { curr_light = mi_api_light_begin($2);
                          light_map = 0; }
                  light_ops
                  END LIGHT
                        { /* 0x26 equals 100110 in binary. We want to select
                           * only the bits that identify the light type, that
                           * is, the bits that tell whether we have an origin,
                           * a direction and a spread value.
                           */
                          switch (light_map & 0x26) {
                            case 0:  /* if nothing is defined, default to
                                      * a point light
                                      */
                            case 2:  /* origin only: point light */
                                    curr_light->type = miLIGHT_ORIGIN;
                                    break;
                            case 4:  /* direction only: directional light */
                                    curr_light->type = miLIGHT_DIRECTION;
                                    break;
                            case 6:  /* origin and direction, no spread:
                                      * directional light with origin
                                      */
                                    curr_light->type = miLIGHT_DIRECTION;
                                    curr_light->dirlight_has_org = miTRUE;
                                    break;
                            case 32: /* spread only: point light */
                            case 34: /* origin and spread, no direction:
                                      * point light
                                      */
                                    curr_light->type = miLIGHT_ORIGIN;
                                    break;
                            case 36: /* direction and spread, no origin:
                                      * directional light
                                      */
                                    curr_light->type = miLIGHT_DIRECTION;
                                    break;
                            case 38: /* origin, direction and spread:
                                      * spot light
                                      */
                                    curr_light->type = miLIGHT_SPOT;
                                    break;
                          }
                          mi_api_light_end(); }
                ;

light_ops       :
                | light_op light_ops
                ;

light_op        : function
                        { if (!(light_map & 1))
                                mi_api_function_delete(&curr_light->shader);
                          light_map |= 1;
                          curr_light->shader = mi_api_function_append(
                                                curr_light->shader, $1); }
                | EMITTER function
                        { if (!(light_map & 8))
                                mi_api_function_delete(&curr_light->emitter);
                          light_map |= 8;
                          curr_light->emitter = mi_api_function_append(
                                                curr_light->emitter, $2); }
                                                        /* hardware_begin */
                | HARDWARE function
                        { if (!(light_map & 16))
                                mi_api_function_delete(&curr_light->hardware);
                          light_map |= 16;
                          curr_light->hardware = mi_api_function_append(
                                                curr_light->hardware, $2); }
                                                        /* hardware_end */
                | SHADOWMAP
                        { curr_light->use_shadow_maps = miTRUE;
                          curr_light->shadowmap_flags = 0; }
                | SHADOWMAP DETAIL
                        { curr_light->use_shadow_maps = miTRUE;
                          curr_light->shadowmap_flags |= miSHADOWMAP_DETAIL; }
                | SHADOWMAP DETAIL SAMPLES T_INTEGER
                        { curr_light->shmap.samples = $4; }
                | SHADOWMAP MERGE
                        { curr_light->shadowmap_flags |= miSHADOWMAP_MERGE; }
                | SHADOWMAP MERGE boolean
                        { if ($3)
                              curr_light->shadowmap_flags |= miSHADOWMAP_MERGE;
                          else
                              curr_light->shadowmap_flags &=~miSHADOWMAP_MERGE;
                          }
                | SHADOWMAP TRACE
                        { curr_light->shadowmap_flags |= miSHADOWMAP_TRACE; }
                | SHADOWMAP TRACE boolean
                        { if ($3)
                              curr_light->shadowmap_flags |= miSHADOWMAP_TRACE;
                          else
                              curr_light->shadowmap_flags &=~miSHADOWMAP_TRACE;
                          }
                | SHADOWMAP WINDOW floating floating floating floating
                        { curr_light->shadowmap_flags |= miSHADOWMAP_CROP;
                          curr_light->shmap_h_min =
                                                (short)miFLOOR($3 * SHRT_MAX);
                          curr_light->shmap_v_min =
                                                (short)miFLOOR($4 * SHRT_MAX);
                          curr_light->shmap_h_max =
                                                (short)miFLOOR($5 * SHRT_MAX);
                          curr_light->shmap_v_max =
                                                (short)miFLOOR($6 * SHRT_MAX);}
                | SHADOWMAP boolean
                        { curr_light->use_shadow_maps = $2;
                          curr_light->shadowmap_flags = 0; }
                | SHADOWMAP CAMERA symbol
                        { mi_api_light_shmap_camera($3); }
                | SHADOWMAP BIAS floating
                        { curr_light->shadowmap_bias = $3; }
                | ORIGIN vector
                        { curr_light->origin = $2;
                          light_map |= 2; }
                | DIRECTION vector
                        { curr_light->direction = $2;
                          mi_vector_normalize(&curr_light->direction);
                          light_map |= 4; }
                | ENERGY colorspace_set color
                        { mi_api_colorprofile_to_renderspace(
                                            &$3, $2, $3.r, $3.g, $3.b);
                          curr_light->energy = $3; }
                | ENERGY SPECTRUM symbol
                        { curr_light->emitter_spectrum 
                                      = mi_api_name_lookup($3);}
                | EXPONENT floating
                        { curr_light->exponent = $2; }
                | CAUSTIC PHOTONS T_INTEGER
                        { curr_light->caustic_store_photons = $3;
                          curr_light->caustic_emit_photons = 0; }
                | CAUSTIC PHOTONS T_INTEGER T_INTEGER
                        { curr_light->caustic_store_photons = $3;
                          curr_light->caustic_emit_photons = $4; }
                | GLOBILLUM PHOTONS T_INTEGER
                        { curr_light->global_store_photons = $3;
                          curr_light->global_emit_photons = 0; }
                | GLOBILLUM PHOTONS T_INTEGER T_INTEGER
                        { curr_light->global_store_photons = $3;
                          curr_light->global_emit_photons = $4; }
                | PHOTONS ONLY boolean
                        { curr_light->photons_only = $3; }
                | RECTANGLE vector vector light_samples
                        { curr_light->area = miLIGHT_RECTANGLE;
                          curr_light->primitive.rectangle.edge_u = $2;
                          curr_light->primitive.rectangle.edge_v = $3; }
                | DISC vector floating light_samples
                        { curr_light->area = miLIGHT_DISC;
                          curr_light->primitive.disc.normal      = $2;
                          curr_light->primitive.disc.radius      = $3; }
                | SPHERE floating light_samples
                        { curr_light->area = miLIGHT_SPHERE;
                          curr_light->primitive.sphere.radius    = $2; }
                | CYLINDER vector floating light_samples
                        { curr_light->area = miLIGHT_CYLINDER;
                          curr_light->primitive.cylinder.axis    = $2;
                          curr_light->primitive.cylinder.radius  = $3; }
                | OBJECT symbol light_samples
                        { curr_light->area = miLIGHT_OBJECT;
                          curr_light->primitive.object.object =
                                mi_api_name_lookup($2); }
                | USER light_samples
                        { curr_light->area = miLIGHT_USER; }
                | RECTANGLE
                        { curr_light->area = miLIGHT_NONE; }
                | DISC
                        { curr_light->area = miLIGHT_NONE; }
                | SPHERE
                        { curr_light->area = miLIGHT_NONE; }
                | CYLINDER
                        { curr_light->area = miLIGHT_NONE; }
                | SPREAD floating
                        { curr_light->spread = $2;
                          light_map |= 32; }
                | SHADOWMAP RESOLUTION T_INTEGER
                        { curr_light->shadowmap_resolution = $3; }
                | SHADOWMAP SOFTNESS floating
                        { curr_light->shadowmap_softness = $3; }
                | SHADOWMAP SAMPLES T_INTEGER
                        { curr_light->shadowmap_samples = $3; }
                | SHADOWMAP FILTER filter_type
                        { curr_light->shmap.filter   = $3;
                          curr_light->shmap.filter_u =
                          curr_light->shmap.filter_v = 0.0; }
                | SHADOWMAP FILTER filter_type floating
                        { curr_light->shmap.filter   = $3;
                          curr_light->shmap.filter_u =
                          curr_light->shmap.filter_v = $4; }
                | SHADOWMAP FILTER filter_type floating floating
                        { curr_light->shmap.filter   = $3;
                          curr_light->shmap.filter_u = $4;
                          curr_light->shmap.filter_v = $5; }
                | SHADOWMAP ACCURACY floating
                        { curr_light->shmap.accuracy = $3; }
                | SHADOWMAP ALPHA
                        { curr_light->shmap.type = 'a'; }
                | SHADOWMAP COLOR
                        { curr_light->shmap.type = 'c'; }
                | SHADOWMAP FILE_ T_STRING
                        { mi_scene_delete(curr_light->shadowmap_file);
                          strcpy((char *)mi_scene_create(
                                        &curr_light->shadowmap_file,
                                        miSCENE_STRING, strlen($3)+1), $3);
                          mi_db_unpin(curr_light->shadowmap_file);
                          mi_api_release($3); }
                | LIGHTPROFILE T_SYMBOL
                        {  if (strcmp($2, "Lambertian")) { 
                                curr_light->lightprofile = 
                                    mi_api_lightprofile_lookup($2);
                                if (curr_light->lightprofile) {
                                    curr_light->use_lprof = miTRUE;
                                } 
                            } else {
                                curr_light->use_lprof = miTRUE;
                            }
                        }
                | VISIBLE
                        { curr_light->visible = miTRUE; }
                | VISIBLE boolean
                        { curr_light->visible = $2; }
                | TAG T_INTEGER
                        { curr_light->label = $2; }
                |       { curr_datatag = &curr_light->userdata; }
                  data
                | dummy_attribute  
                ;

light_samples   :
                | T_INTEGER
                        { curr_light->samples_u     = $1;
                          curr_light->samples_v     = 1;  }
                | T_INTEGER T_INTEGER
                        { curr_light->samples_u     = $1;
                          curr_light->samples_v     = $2; }
                | T_INTEGER T_INTEGER T_INTEGER
                        { curr_light->samples_u     = $1;
                          curr_light->samples_v     = $2;
                          curr_light->low_level     = $3; }
                | T_INTEGER T_INTEGER T_INTEGER T_INTEGER T_INTEGER
                        { curr_light->samples_u     = $1;
                          curr_light->samples_v     = $2;
                          curr_light->low_level     = $3;
                          curr_light->low_samples_u = $4;
                          curr_light->low_samples_v = $5; }
                ;


/*-----------------------------------------------------------------------------
 * material
 *---------------------------------------------------------------------------*/

material        : MATERIAL symbol
                        { curr_mtl = mi_api_material_begin($2);
                          have_d = have_s = have_v = have_e = have_c =
                          have_p = have_pv = have_lm = have_hw = 0; }
                  mtl_flags
                  mtl_shader
                  mtl_args
                  END MATERIAL
                        { mi_api_material_end(); }
                ;

mtl_shader      :
                |
                  function_list
                        { curr_mtl->shader = $1; }
                ;

mtl_flags       :
                | mtl_flag mtl_flags
                ;

mtl_flag        : NOCONTOUR
                        { mi_api_warning(
                                "obsolete \"nocontour\" flag ignored"); }
                | OPAQUE_
                        { curr_mtl->opaque = miTRUE; }
                | dummy_attribute       
                ;

mtl_args        :
                | mtl_arg mtl_args
                ;

mtl_arg         : DISPLACE
                        { mi_api_function_delete(&curr_mtl->displace); }
                | DISPLACE
                        { if (!have_d++)
                                mi_api_function_delete(&curr_mtl->displace); }
                  function_list         
                        { curr_mtl->displace = $3; }
                | SHADOW
                        { mi_api_function_delete(&curr_mtl->shadow); }
                | SHADOW
                        { if (!have_s++)
                                mi_api_function_delete(&curr_mtl->shadow); }
                  function_list
                        {  curr_mtl->shadow = $3; }
                | VOLUME
                        { mi_api_function_delete(&curr_mtl->volume); }
                | VOLUME
                        { if (!have_v++) 
                                mi_api_function_delete(&curr_mtl->volume); }
                  function_list         
                        { curr_mtl->volume = $3; }
                | ENVIRONMENT
                        { mi_api_function_delete(&curr_mtl->environment); }
                | ENVIRONMENT
                        { if (!have_e++)
                                mi_api_function_delete(&curr_mtl->environment); }
                  function_list 
                        { curr_mtl->environment = $3; }
                | CONTOUR
                        { mi_api_function_delete(&curr_mtl->contour); }
                | CONTOUR
                        { if (!have_c++)
                                mi_api_function_delete(&curr_mtl->contour); }
                  function_list          
                        { curr_mtl->contour = $3; }
                | PHOTON
                        { mi_api_function_delete(&curr_mtl->photon); }
                | PHOTON
                        { if (!have_p++)
                                mi_api_function_delete(&curr_mtl->photon); }
                  function_list                 
                        { curr_mtl->photon = $3; }
                | PHOTONVOL
                        { mi_api_function_delete(&curr_mtl->photonvol); }
                | PHOTONVOL
                        { if (!have_pv++)
                                mi_api_function_delete(&curr_mtl->photonvol); }
                  function_list
                        { curr_mtl->photonvol = $3; }
                | LIGHTMAP
                        { mi_api_function_delete(&curr_mtl->lightmap); }
                | LIGHTMAP
                        { if (!have_lm++)
                                mi_api_function_delete(&curr_mtl->lightmap); }
                 function_list  
                        { curr_mtl->lightmap = $3; }
                                                        /* hardware_begin */
                | HARDWARE
                        { mi_api_function_delete(&curr_mtl->hardware); }
                | HARDWARE
                        { if (!have_hw++)
                                mi_api_function_delete(&curr_mtl->hardware); }
                  function_list
                        { curr_mtl->hardware = $3; }
                                                        /* hardware_end */
                ;


                                                        /* smallparser_begin */
/*-----------------------------------------------------------------------------
 * object
 *---------------------------------------------------------------------------*/

object          : OBJECT
                        { mi_get_filepos(&filepos, &filename); filepos-=7; }
                  opt_symbol
                        { if (mi_reload_parsing()) {
                                mi_api_incremental(miTRUE);
                                curr_obj = mi_api_object_begin($3);
                          } else {
                            curr_obj = mi_api_object_begin_r(
                                $3, mi_api_strdup(filename), filepos); } }
                  obj_flags
                  object_body
                  END OBJECT
                        { mi_api_object_end(); mi_end_object(); }
                ;

obj_flags       :
                | obj_flags obj_flag
                ;

obj_flag        : VISIBLE
                        { curr_obj->visible      = miTRUE; }
                | VISIBLE boolean
                        { curr_obj->visible      = $2; }
                | SHADOW
                        { curr_obj->shadow       = 0x03; }
                | SHADOW boolean
                        { curr_obj->shadow       = $2 ? 0x03 : 0x02; }
                | SHADOW T_INTEGER
                        { curr_obj->shadow       = ($2 & 0x03); }
                | SHADOWMAP
                        { curr_obj->shadowmap    = miTRUE; }
                | SHADOWMAP boolean
                        { curr_obj->shadowmap    = $2; }
                | TRACE
                        { curr_obj->reflection   =
                          curr_obj->refraction   =
                          curr_obj->finalgather  = 0x03; }
                | TRACE boolean
                        { curr_obj->reflection   =
                          curr_obj->refraction   =
                          curr_obj->finalgather  = $2 ? 0x03 : 0x02; }
                | REFLECTION T_INTEGER
                        { curr_obj->reflection   = ($2 & 0x03); }
                | REFRACTION T_INTEGER
                        { curr_obj->refraction   = ($2 & 0x03); }
                | TRANSPARENCY T_INTEGER
                        { curr_obj->transparency = ($2 & 0x03); }
                | FACE FRONT
                        { curr_obj->face         = 'f'; }
                | FACE BACK
                        { curr_obj->face         = 'b'; }
                | FACE BOTH
                        { curr_obj->face         = 'a'; }
                | SELECT
                        { curr_obj->select       = miTRUE; }
                | SELECT boolean
                        { curr_obj->select       = $2; }
                | TAGGED
                        { curr_obj->mtl_is_label = miTRUE; }
                | TAGGED boolean
                        { curr_obj->mtl_is_label = $2; }
                | CAUSTIC
                        { curr_obj->caustic     |= 3; }
                | CAUSTIC boolean
                        { curr_obj->caustic     &= 0x03;
                          if (!$2) curr_obj->caustic |= 0x10; }
                | CAUSTIC T_INTEGER
                        { curr_obj->caustic     &= 0x10;
                          curr_obj->caustic     |= ($2 & 0x03); }
                | GLOBILLUM
                        { curr_obj->globillum   |= 3; }
                | GLOBILLUM boolean
                        { curr_obj->globillum   &= 0x03;
                          if (!$2) curr_obj->globillum |= 0x10; }
                | GLOBILLUM T_INTEGER
                        { curr_obj->globillum   &= 0x10;
                          curr_obj->globillum   |= ($2 & 0x03); }
                | PHOTONMAP FILE_
                        { mi_scene_delete(curr_obj->photonmap_file);
                          curr_obj->photonmap_file = miNULLTAG; } 
                | PHOTONMAP FILE_ OFF
                        { mi_scene_delete(curr_obj->photonmap_file);
                          curr_obj->photonmap_file = miNULLTAG; } 
                | PHOTONMAP FILE_ T_STRING
                        {  mi_scene_delete(curr_obj->photonmap_file);
                           if (($3)[0]) {
                                strcpy((char *)mi_scene_create(
                                        &curr_obj->photonmap_file,
                                        miSCENE_STRING, strlen($3)+1), $3);
                                mi_scene_edit_end(curr_obj->photonmap_file);
                            } else {
                                curr_obj->photonmap_file = miNULLTAG; 
                            } 
                           mi_api_release($3); }
                | FINALGATHER boolean
                        { curr_obj->finalgather &= 0x03;
                          if (!$2) curr_obj->finalgather |= 0x10; }
                | FINALGATHER T_INTEGER
                        { curr_obj->finalgather &= 0x10;
                          curr_obj->finalgather |= ($2 & 0x03); }
                | FINALGATHER FILE_ map_list
                        { mi_api_taglist_reset(&curr_obj->finalgather_file,
                                               $3); }
                                                        /* hardware_begin */
                | SHADING SAMPLES floating
                        { curr_obj->shading_samples = $3; }
                | HARDWARE
                        { curr_obj->hardware = miTRUE; }
                | HARDWARE boolean
                        { curr_obj->hardware = $2; }
                                                        /* hardware_end */
                | TAG T_INTEGER
                        { curr_obj->label = $2; }
                |       { curr_datatag = &curr_obj->userdata; }
                  data
                | transform
                        { mi_api_object_matrix($1); }
                | MAX_ DISPLACE floating
                        { curr_obj->maxdisplace = $3; }
                | RAY_ OFFSET floating
                        {curr_obj->ray_offset = $3; }
                | BOX vector vector
                        { curr_obj->bbox_min = $2;
                          curr_obj->bbox_max = $3; }
                | BOX
                        { curr_obj->bbox_min = nullvec;
                          curr_obj->bbox_max = nullvec; }
                | MOTION BOX vector vector
                        { curr_obj->bbox_min_m = $3;
                          curr_obj->bbox_max_m = $4; }
                | MOTION BOX
                        { curr_obj->bbox_min_m = nullvec;
                          curr_obj->bbox_max_m = nullvec; }
                | SAMPLES T_INTEGER
                        { curr_obj->min_samples = $2-2;
                          curr_obj->max_samples = $2;}
                | SAMPLES T_INTEGER T_INTEGER
                        { curr_obj->min_samples = $2;
                          curr_obj->max_samples = $3;}
                | VOLUME GROUP T_INTEGER
                        { curr_obj->volume_id = $3; }
                | dummy_attribute       
                ;

object_body     : bases_and_groups
                | FILE_ T_STRING
                        { mi_api_object_file($2); }
                | hair_object
                | trilist_object
                | isect_object
                ;

bases_and_groups:
                | basis bases_and_groups
                | group bases_and_groups
                ;

basis           : BASIS symbol rational MATRIX T_INTEGER T_INTEGER basis_matrix
                        { mi_api_basis_add($2, $3, miBASIS_MATRIX, $5,$6,$7); }
                | BASIS symbol rational BEZIER T_INTEGER
                        { mi_api_basis_add($2, $3, miBASIS_BEZIER, $5, 0, 0); }
                | BASIS symbol rational TAYLOR T_INTEGER
                        { mi_api_basis_add($2, $3, miBASIS_TAYLOR, $5, 0, 0); }
                | BASIS symbol rational BSPLINE T_INTEGER
                        { mi_api_basis_add($2, $3, miBASIS_BSPLINE, $5, 0, 0);}
                | BASIS symbol rational CARDINAL
                        { mi_api_basis_add($2, $3, miBASIS_CARDINAL, 3, 0, 0);}
                ;

rational        :
                        { $$ = miFALSE; }
                | RATIONAL
                        { $$ = miTRUE; }
                ;

basis_matrix    :       { $$ = mi_api_dlist_create(miDLIST_GEOSCALAR); }
                | basis_matrix floating
                        { miGeoScalar s=$2; mi_api_dlist_add($1, &s); $$=$1; }
                ;

group           : GROUP opt_symbol merge_option
                        { mi_api_object_group_begin($3);
                          mi_api_release($2); }
                  vector_list
                  vertex_list
                  geometry_list
                  END GROUP
                        { mi_api_object_group_end(); }
                ;

merge_option    :
                        { $$ = 0.0; }
                | MERGE floating
                        { $$ = $2; }
                ;

vector_list     :
                | vector_list geovector
                        { mi_api_geovector_xyz_add(&$2); }
                ;

vertex_list     :
                | vertex_list vertex
                ;

vertex          : V_ T_INTEGER
                        { mi_api_vertex_add($2); }
                  n_vector
                  d_vector
                  t_vector_list
                  m_vector_list
                  u_vector_list
                  vertex_flag
                ;

n_vector        :
                | N T_INTEGER
                        { mi_api_vertex_normal_add($2); }
                ;

d_vector        :
                | D T_INTEGER T_INTEGER
                        { mi_api_vertex_deriv_add($2, $3); }
                | D T_INTEGER T_INTEGER T_INTEGER
                        { mi_api_vertex_deriv2_add($2, $3, $4); }
                | D T_INTEGER T_INTEGER T_INTEGER T_INTEGER T_INTEGER
                        { mi_api_vertex_deriv_add($2, $3);
                          mi_api_vertex_deriv2_add($4, $5, $6); }
                ;

m_vector_list   :
                | m_vector_list M T_INTEGER
                        { mi_api_vertex_motion_add($3); }
                ;

t_vector_list   :
                | t_vector_list T_ T_INTEGER
                        { mi_api_vertex_tex_add($3, -1, -1); }
                | t_vector_list T_ T_INTEGER T_INTEGER T_INTEGER
                        { mi_api_vertex_tex_add($3, $4, $5); }
                ;

u_vector_list   :
                | u_vector_list U_ T_INTEGER
                        { mi_api_vertex_user_add($3); }
                ;

vertex_flag     :
                | CUSP
                        { mi_api_vertex_flags_add(miAPI_V_CUSP, 0, 1.f); }
                | CUSP LEVEL T_INTEGER
                        { mi_api_vertex_flags_add(miAPI_V_CUSP, $3, 1.f); }
                | CONIC
                        { mi_api_vertex_flags_add(miAPI_V_CONIC, 0, 1.f); }
                | CONIC LEVEL T_INTEGER
                        { mi_api_vertex_flags_add(miAPI_V_CONIC, $3, 1.f); }
                | CORNER
                        { mi_api_vertex_flags_add(miAPI_V_CORNER, 0, 1.f); }
                | CORNER LEVEL T_INTEGER
                        { mi_api_vertex_flags_add(miAPI_V_CORNER, $3, 1.f); }
                | DART
                        { mi_api_vertex_flags_add(miAPI_V_DART, 0, 0.f); }
                ;

geometry_list   :
                | geometry_list geometry
                ;

geometry        : polygon
                | curve
                | spacecurve
                | surface
                | subdivsurf
                | ccmesh
                | connection
                | approximation
                ;


/* polygons */

polygon         : CP opt_symbol
                        { mi_api_poly_begin(1, $2); }
                  poly_indices
                        { mi_api_poly_end(); }
                | P_ opt_symbol
                        { mi_api_poly_begin(0, $2); }
                  poly_indices
                        { mi_api_poly_end(); }
                | STRIP opt_symbol
                        { mi_api_poly_begin(2, $2); }
                  strip_indices
                        { mi_api_poly_end(); }
                | FAN opt_symbol
                        { mi_api_poly_begin(3, $2); }
                  strip_indices
                        { mi_api_poly_end(); }
                ;

poly_indices    :
                | T_INTEGER
                        { mi_api_poly_index_add($1); }
                  poly_indices
                | HOLE
                        { mi_api_poly_hole_add(); }
                  poly_indices
                ;

strip_indices   :
                | T_INTEGER
                        { mi_api_poly_index_add($1); }
                  strip_indices
                ;

h_vertex_ref_seq: h_vertex_ref
                | h_vertex_ref_seq h_vertex_ref
                ;

h_vertex_ref    : T_INTEGER
                        { mi_api_vertex_ref_add($1, (double)1.0); }
                | T_INTEGER T_FLOAT
                        { mi_api_vertex_ref_add($1, $2); }
                | T_INTEGER W_ floating
                        { mi_api_vertex_ref_add($1, $3); }
                ;


para_list       : T_FLOAT
                        { miDlist *dlp =mi_api_dlist_create(miDLIST_GEOSCALAR);
                          miGeoScalar s = $1;   /* $1 is a double */
                          mi_api_dlist_add(dlp, &s);
                          $$ = dlp; }
                | para_list T_FLOAT
                        { miGeoScalar s = $2;   /* $2 is a double */
                          mi_api_dlist_add($1, &s);
                          $$ = $1; }
                ;


/* curves and space curves */

curve           : CURVE symbol rational symbol
                        { mi_api_curve_begin($2, $4, $3); }
                  para_list h_vertex_ref_seq curve_spec
                        { mi_api_curve_end($6); }
                ;

curve_spec      :
                | SPECIAL curve_special_list
                ;

curve_special_list
                : curve_special
                | curve_special_list curve_special
                ;

curve_special   : T_INTEGER
                        { mi_api_curve_specpnt($1, -1); }
                | T_INTEGER MAPSTO T_INTEGER
                        { mi_api_curve_specpnt($1, $3); }
                ;

spacecurve      : SPACE CURVE symbol
                        { mi_api_spacecurve_begin($3); }
                  spcurve_list
                        { mi_api_spacecurve_end(); }
                ;

spcurve_list    : symbol floating floating
                        { miGeoRange r;
                          r.min = $2;
                          r.max = $3;
                          mi_api_spacecurve_curveseg(miTRUE, $1, &r); }
                | spcurve_list symbol floating floating
                        { miGeoRange r;
                          r.min = $3;
                          r.max = $4;
                          mi_api_spacecurve_curveseg(miFALSE, $2, &r); }
                ;


/* free-form surfaces */

surface         : SURFACE symbol mtl_or_label
                        { mi_api_surface_begin($2, $3); }
                  rational symbol floating floating para_list
                        { mi_api_surface_params(miU, $6, $7, $8, $9, $5); }
                  rational symbol floating floating para_list
                        { mi_api_surface_params(miV, $12, $13, $14, $15, $11);}
                  h_vertex_ref_seq
                  tex_surf_list
                  surf_spec_list
                        { mi_api_surface_end(); }
                ;

mtl_or_label    : symbol
                        { $$ = $1; }
                | T_INTEGER
                        { $$ = (char *)(miIntptr)$1; }
                ;

tex_surf_list   :
                | tex_surf_list tex_surf
                ;

tex_surf        : opt_volume_flag opt_vector_flag TEXTURE
                  rational symbol para_list
                  rational symbol para_list
                        { mi_api_surface_texture_begin(
                                        $1, $2, $5, $6, $4, $8, $9, $7); }
                  h_vertex_ref_seq

                | DERIVATIVE
                        { mi_api_surface_derivative(1); }
                | DERIVATIVE T_INTEGER
                        { mi_api_surface_derivative($2); }
                | DERIVATIVE T_INTEGER T_INTEGER
                        { mi_api_surface_derivative($2);
                          mi_api_surface_derivative($3); }
                ;

opt_volume_flag :
                        { $$ = miFALSE; }
                | VOLUME
                        { $$ = miTRUE; }
                ;

opt_vector_flag :
                        { $$ = miFALSE; }
                | VECTOR
                        { $$ = miTRUE; }
                ;


surf_spec_list  :
                | surf_spec_list surf_spec
                ;

surf_spec       : TRIM trim_spec_list
                | HOLE hole_spec_list
                | SPECIAL
                        { newloop = miTRUE; }
                  special_spec_list
                ;

trim_spec_list  : symbol floating floating
                        { miGeoRange r;
                          r.min = $2;
                          r.max = $3;
                          mi_api_surface_curveseg(miTRUE, miCURVE_TRIM,$1,&r);}
                | trim_spec_list symbol floating floating
                        { miGeoRange r;
                          r.min = $3;
                          r.max = $4;
                          mi_api_surface_curveseg(miFALSE,miCURVE_TRIM,$2,&r);}
                ;

hole_spec_list  : symbol floating floating
                        { miGeoRange r;
                          r.min = $2;
                          r.max = $3;
                          mi_api_surface_curveseg(miTRUE,miCURVE_HOLE,$1,&r); }
                | hole_spec_list symbol floating floating
                        { miGeoRange r;
                          r.min = $3;
                          r.max = $4;
                          mi_api_surface_curveseg(miFALSE,miCURVE_HOLE,$2,&r);}
                ;

special_spec_list
                : special_spec
                | special_spec_list special_spec
                ;

special_spec    : T_INTEGER
                        { mi_api_surface_specpnt($1, -1); }
                | T_INTEGER MAPSTO T_INTEGER
                        { mi_api_surface_specpnt($1, $3); }
                | symbol floating floating
                        { miGeoRange r;
                          r.min = $2;
                          r.max = $3;
                          mi_api_surface_curveseg(newloop,
                                                  miCURVE_SPECIAL, $1, &r);
                          newloop = miFALSE; }
                ;

connection      : CONNECT
                  symbol symbol floating floating
                  symbol symbol floating floating
                        { miGeoRange c1, c2;
                          c1.min = $4;
                          c1.max = $5;
                          c2.min = $8;
                          c2.max = $9;
                          mi_api_object_group_connection($2,$3,&c1,$6,$7,&c2);}
                ;


/* subdivision surfaces */


subdivsurf      : SUBDIVISION SURFACE
                        { memset(&subdiv_opt, 0, sizeof(subdiv_opt)); }
                  sds_surf
                  sds_base_faces
                  derivatives
                  END SUBDIVISION SURFACE
                        { mi_api_subdivsurf_end(); }
                ;

sds_surf        : symbol sds_specs
                        { mi_api_subdivsurf_begin_x($1, &subdiv_opt); }

sds_specs       :
                | sds_specs sds_spec
                ;

sds_spec        : POLYGON T_INTEGER T_INTEGER T_INTEGER T_INTEGER
                        { subdiv_opt.no_basetris  = $2;
                          subdiv_opt.no_hiratris  = $3;
                          subdiv_opt.no_basequads = $4;
                          subdiv_opt.no_hiraquads = $5;
                          subdiv_opt.no_vertices  = 0; }
                | TEXTURE SPACE
                        { texspace_idx = 0; }
                  '[' texspace ']'
                        { mi_api_subdivsurf_texspace(subdiv_texspace,
                                                     texspace_idx); }
                ;

texspace        : FACE texspace_nxt
                        { subdiv_texspace[texspace_idx++].face = miTRUE; }
                | SUBDIVISION texspace_nxt
                        { subdiv_texspace[texspace_idx++].face = miFALSE; }
                ;

texspace_nxt    :
                | ','
                | ',' texspace
                ;

derivatives     :
                | derivatives derivative
                ;

derivative      : DERIVATIVE T_INTEGER
                        { mi_api_subdivsurf_derivative($2, 0); }
                | DERIVATIVE T_INTEGER SPACE T_INTEGER
                        { mi_api_subdivsurf_derivative($2, $4); }
                ;

sds_base_faces  :
                | sds_base_faces sds_base_face
                ;

sds_base_face   : P_ opt_symbol sds_indices
                        { mi_api_subdivsurf_baseface();
                          mi_api_subdivsurf_mtl(-1, $2); }
                  base_data
                ;

base_data       :
                | base_spec base_data
                ;

base_spec       : '{'
                        { mi_api_subdivsurf_push();
                          mi_api_subdivsurf_subdivide(-1); }
                  hira_data '}'
                        { mi_api_subdivsurf_pop(); }
                | CREASE T_INTEGER sds_creaseflags
                        { mi_api_subdivsurf_crease(-1, $2); }
                | TRIM T_INTEGER
                        { mi_api_subdivsurf_trim(-1, $2); }
                ;

hira_data       :
                | hira_spec hira_data
                ;

hira_spec       : MATERIAL T_INTEGER symbol
                        { mi_api_subdivsurf_mtl($2, $3); }
                | MATERIAL T_INTEGER T_INTEGER
                        { mi_api_subdivsurf_mtl_tag($2, $3); }
                | DETAIL T_INTEGER sds_indices
                        { mi_api_subdivsurf_detail($2); }
                | CREASE T_INTEGER T_INTEGER sds_creaseflags
                        { mi_api_subdivsurf_crease($2, $3); }
                | TRIM T_INTEGER T_INTEGER
                        { mi_api_subdivsurf_trim($2, $3); }
                | CHILD T_INTEGER '{'
                        { mi_api_subdivsurf_push();
                          mi_api_subdivsurf_subdivide($2); }
                  hira_data '}'
                        { mi_api_subdivsurf_pop(); }
                ;

sds_indices     :
                | T_INTEGER
                        { mi_api_subdivsurf_index($1); }
                  sds_indices
                ;

sds_creaseflags :
                | floating
                        { mi_api_subdivsurf_crease_edge($1); }
                  sds_creaseflags
                ;


/* ccmesh surfaces */

ccmesh          : CCMESH symbol
                  POLYGON T_INTEGER VERTEX T_INTEGER
                        { miApi_ccmesh_options opt;
                          opt.no_polygons = $4;
                          opt.no_vertices = $6;
                          mi_api_ccmesh_begin($2, &opt);
                          ccmesh_nvtx    = 0;
                          ccmesh_ncrease = 0;
                          ccmesh_mtl     = 0;
                          ccmesh_needslabel = curr_obj->mtl_is_label; }
                  ccmesh_polys
                  ccmesh_derivs
                  END CCMESH
                        { mi_api_ccmesh_end(); ccmesh_mtl = 0; }
                  ;

ccmesh_polys    : P_ symbol ccmesh_vertices
                        { ccmesh_mtl = mi_api_material_lookup($2);
                          mi_api_ccmesh_polygon(ccmesh_nvtx,
                                    ctx->ccmesh_vtx, ccmesh_mtl);
                          ccmesh_nvtx = 0; }
                  ccmesh_crease
                  ccmesh_sym
                | P_
                        { ccmesh_label = ccmesh_needslabel; }
                  ccmesh_vertices
                        { 
                          mi_api_ccmesh_polygon(ccmesh_nvtx,
                                    ctx->ccmesh_vtx, ccmesh_mtl);
                          ccmesh_nvtx = 0; }
                  ccmesh_crease
                  ccmesh_nosym
                ;

ccmesh_sym      :
                | ccmesh_sym P_ opt_symbol ccmesh_vertices
                        { if ($3)
                                ccmesh_mtl = mi_api_material_lookup($3);
                          mi_api_ccmesh_polygon(ccmesh_nvtx,
                                    ctx->ccmesh_vtx, ccmesh_mtl);
                          ccmesh_nvtx = 0; }
                  ccmesh_crease
                ;

ccmesh_nosym    :
                | ccmesh_nosym P_
                        { ccmesh_label = ccmesh_needslabel; }
                  ccmesh_vertices
                        { mi_api_ccmesh_polygon(ccmesh_nvtx,
                                    ctx->ccmesh_vtx, ccmesh_mtl);
                          ccmesh_nvtx = 0; }
                  ccmesh_crease
                ;

ccmesh_vertices :
                | ccmesh_vertices T_INTEGER
                        { if (ccmesh_label) {
                                ccmesh_mtl = $2;
                                ccmesh_label = miFALSE;
                          } else {
                                if (ccmesh_nvtx+1 > ctx->ccmesh_vtx_size) {
                                        ctx->ccmesh_vtx_size =
                                                ctx->ccmesh_vtx_size * 3 / 2;
                                        ctx->ccmesh_vtx = (miUint*)
                                                        mi_api_reallocate(
                                        ctx->ccmesh_vtx,
                                        sizeof(miUint) * ctx->ccmesh_vtx_size);
                                }
                                ctx->ccmesh_vtx[ccmesh_nvtx++] = $2; } }
                ;

ccmesh_crease   :
                | CREASE ccmesh_cvalues
                        { mi_api_ccmesh_crease(ctx->ccmesh_crease);
                          ccmesh_ncrease = 0; }
                ;

ccmesh_cvalues  :
                | ccmesh_cvalues floating
                        { if (ccmesh_ncrease+1 > ctx->ccmesh_crease_size) {
                                ctx->ccmesh_crease_size =
                                        ctx->ccmesh_crease_size * 3 / 2;
                                ctx->ccmesh_crease = (miScalar*)
                                                        mi_api_reallocate(
                                    ctx->ccmesh_crease, sizeof(miScalar) *
                                    ctx->ccmesh_crease_size);
                          }
                          ctx->ccmesh_crease[ccmesh_ncrease++] = $2; }
                ;

ccmesh_derivs   :
                | ccmesh_derivs ccmesh_deriv
                ;

ccmesh_deriv    : DERIVATIVE T_INTEGER
                        { mi_api_ccmesh_derivative($2, 0); }
                | DERIVATIVE T_INTEGER SPACE T_INTEGER                
                        { mi_api_ccmesh_derivative($2, $4); }
                ;


/* hairs */

hair_object     : HAIR
                        { hair = mi_api_hair_begin(); }
                  hair_options
                  SCALAR '[' T_INTEGER ']'
                        { hair_index   = 0;
                          hair_scalars = mi_api_hair_scalars_begin($6); }
                  hair_scalars
                        { mi_api_hair_scalars_end(hair_index); }
                  HAIR '[' T_INTEGER ']'
                        { hair_indices = mi_api_hair_hairs_begin($13); }
                  hair_hairs
                        { mi_api_hair_hairs_end();
                          mi_api_hair_end(); }
                  END HAIR

hair_options    : hair_option hair_options
                |
                ;

hair_option     : MATERIAL symbol
                        { hair->material = mi_api_material_lookup($2); }
                | RADIUS floating
                        { hair->radius = $2; }
                | APPROXIMATE T_INTEGER
                        { hair->approx = $2; }
                | DEGREE T_INTEGER
                        { hair->degree = $2; }
                | MAX_ SIZE T_INTEGER
                        { hair->space_max_size  = $3; }
                | MAX_ DEPTH T_INTEGER
                        { hair->space_max_depth = $3; }
                | HAIR N
                        { mi_api_hair_info(0, 'n', 3); }
                | HAIR M T_INTEGER
                        { mi_api_hair_info(0, 'm', 3*$3); }
                | HAIR T_ T_INTEGER
                        { mi_api_hair_info(0, 't', $3); }
                | HAIR RADIUS
                        { mi_api_hair_info(0, 'r', 1); }
                | HAIR U_ T_INTEGER
                        { mi_api_hair_info(0, 'u', $3); }
                | VERTEX N
                        { mi_api_hair_info(1, 'n', 3); }
                | VERTEX M T_INTEGER
                        { mi_api_hair_info(1, 'm', 3*$3); }
                | VERTEX T_ T_INTEGER
                        { mi_api_hair_info(1, 't', $3); }
                | VERTEX RADIUS
                        { mi_api_hair_info(1, 'r', 1); }
                | VERTEX U_ T_INTEGER
                        { mi_api_hair_info(1, 'u', $3); }
                ;

hair_scalars    : BINARY
                        { ctx->read_integer = hair->no_scalars;
                          ctx->ri_buf = (int*)hair_scalars; }
                  T_VECTOR
                        { hair_index  = hair->no_scalars; }
                | hair_scalars_a
                ;

hair_scalars_a  :
                | hair_scalars_a floating
                        { if (hair_index < hair->no_scalars)
                                hair_scalars[hair_index] = $2;
                          hair_index++; }
                ;

hair_hairs      : BINARY
                        { ctx->read_integer = hair->no_hairs+1;
                          ctx->ri_buf = (int*)hair_indices; }
                  T_VECTOR
                | hair_hairs_a
                ;

hair_hairs_a    :
                | hair_hairs_a T_INTEGER
                        { mi_api_hair_hairs_add($2); }
                ;


/* trilists */

trilist_object  : TRILIST
                        { memset(&tlcont, 0, sizeof(tlcont));
                          tlcont.sizeof_vertex++; }
                  VECTOR '[' T_INTEGER ']'
                  VERTEX '[' T_INTEGER ']' P_
                        tl_specs
                  TRIANGLE '[' T_INTEGER ']'
                        { tlbox = mi_api_trilist_begin(&tlcont,
                                        $5, $9, $15);
                          tlvec     = tlbox->vectors;
                          tlvert    = miBOX_GET_VERTICES(tlbox);
                          tlvec_idx = tlvert_idx = tl_ind = 0;
                          tl_nvec   = $5;
                          tl_nvert  = $9 * tlcont.sizeof_vertex;
                          tl_nind   = tlbox->mtl_is_label ? 4 : 3; }
                  '[' tl_vectors   ']'
                  '[' tl_vertices  ']'
                  '[' tl_triangles ']'
                  END TRILIST
                        { mi_api_trilist_end(); }
                  tl_approx
                | TRILIST VERTEX T_INTEGER P_           /* new in 3.4 */
                        { memset(&plinfo, 0, sizeof(plinfo));
                          plinfo.line_size = 3;
                          pl_priminfosize = 0;
                          pl_primdatasize = 0; }
                  pl_specs
                  TRIANGLE T_INTEGER pl_border pl_priminfo
                        { miUint no_prims = $8 + $9;
                          miUint no_plist = $9 ? 2 : 1;
                          plbox = mi_api_primlist_begin_2(&plinfo,
                                        $3, no_plist, no_prims * 3,
                                        no_prims,       /* no_materials */
                                        pl_primdatasize,/* primdata_size */
                                        pl_priminfosize,/* pd_info_size */
                                        no_prims);
                          if ($9)
                                mi_api_primlist_border(1, $9);
                          pllines = miBOX_VERTEX_LINES(plbox);
                          plprims = miBOX_PRIMS(plbox);
                          plmtls  = miBOX_MATERIALS(plbox);
                          pl_priminfo = miBOX_PD_INFO(plbox);
                          pl_primdata = miBOX_PRIMDATA(plbox);
                          *plprims++ = miSCENE_PRIMLIST_MAKE_CODE(
                                        miSCENE_PRIM_TRI, $8 * 3);
                          mi_api_primlist_dimensions(pl_texo, pl_uso);
                          tl_nind = plbox->mtl_is_label ? 4 : 3;
                          tl_ind = 0; pl_no_prims = $8; }
                  pl_lines
                  pl_prims
                  pl_borderprims
                  pl_primdata
                  pl_topology
                  END TRILIST
                        { miUint no_prims = $8 + $9;
                          miUint no_plist = $9 ? 2 : 1;
                          mi_api_primlist_end();
                          if (plprims != miBOX_PRIMS(plbox)+
                              no_prims*3+no_plist)
                                mi_api_error("wrong number of triangles");
                          if (pllines != miBOX_VERTEX_LINES(plbox) + $3 *
                              plinfo.line_size)
                                mi_api_error("wrong number of scalars");
                          if (pl_priminfo !=
                              miBOX_PD_INFO(plbox) + pl_priminfosize)
                                mi_api_error("wrong prim info size");
                          if (pl_primdata !=
                              miBOX_PRIMDATA(plbox) +
                              pl_primdatasize * no_prims)
                                mi_api_error("wrong prim data size"); }
                  tl_approx
                ;

/* new trilists 3.4 */

pl_topology     :
                | TOPOLOGY
                        { pltop = (miUint*) mi_api_allocate(sizeof(miUint) *
                                                plbox->no_prims*3);
                          cur_pltop = pltop; }
                  pl_top
                        { mi_api_primlist_topology(pltop);
                          mi_api_release(pltop); }
                ;

pl_top          : '[' pl_top_ascii ']'
                | INTEGER
                        { ctx->read_integer = plbox->no_prims*3;
                          ctx->ri_buf = (int*)pltop; }
                  T_VECTOR
                ;

pl_top_ascii    :
                | pl_top_ascii T_INTEGER
                        { *cur_pltop++ = $2; }
                ;

pl_border       :
                        { $$ = 0; }
                | BORDER T_INTEGER
                        { $$ = $2; }
                ;

pl_priminfo     :
                | DATA T_INTEGER T_INTEGER
                        { pl_priminfosize = $2; pl_primdatasize = $3; }
                ;

pl_primdata     :
                | TRIANGLE DATA '[' pl_priminfodata_a ']'
                                '[' pl_primdata_a ']'
                | TRIANGLE DATA INTEGER
                        { ctx->read_integer = pl_priminfosize;
                          ctx->ri_buf = (int*)pl_priminfo; }
                    T_VECTOR INTEGER
                        { ctx->read_integer =
                                pl_primdatasize * plbox->no_prims;
                          ctx->ri_buf = (int*)pl_primdata; }
                    T_VECTOR
                        { pl_priminfo += pl_priminfosize;
                          pl_primdata += pl_primdatasize * plbox->no_prims; }
                ;

pl_priminfodata_a:
                | pl_priminfodata_a T_INTEGER
                        { *pl_priminfo++ = $2; }
                ;

pl_primdata_a   :
                | pl_primdata_a T_INTEGER
                        { *pl_primdata++ = $2; }
                ;

pl_lines        : SCALAR
                        { ctx->read_integer = plinfo.line_size *
                                        miBOX_NO_VTXLINES(plbox);
                          ctx->ri_buf = (int*)pllines; }
                  T_VECTOR
                        { pllines += plinfo.line_size *
                                        miBOX_NO_VTXLINES(plbox); }
                | '[' pl_ascii_lines ']'
                ;

pl_ascii_lines  :
                | pl_ascii_lines floating
                        { *pllines++ = $2; }
                ;

pl_borderprims  :
                | { *plprims++ = miSCENE_PRIMLIST_MAKE_CODE(
                                        miSCENE_PRIM_TRI,
                                        plbox->no_border_prims * 3);
                    pl_no_prims = plbox->no_border_prims;
                  } pl_prims
                ;

pl_prims        : '[' symbol T_INTEGER T_INTEGER T_INTEGER
                        { *plmtls++ = mi_api_material_lookup($2);
                          *plprims++ = $3; *plprims++ = $4;
                          *plprims++ = $5; }
                  pl_tri_mtl
                  ']'
                | pl_tri_index
                ;

pl_tri_mtl      :
                | pl_tri_mtl opt_symbol T_INTEGER T_INTEGER T_INTEGER
                        { *plmtls++ = ($2) ? mi_api_material_lookup($2)
                                           : *(plmtls-2);
                          *plprims++ = $3; *plprims++ = $4;
                          *plprims++ = $5; }
                ;

pl_tri_index    : INTEGER
                        { if (tl_nind != 4)
                                mi_api_error("binary triangles/no "
                                                "tagged mode");
                          ctx->read_integer = pl_no_prims*3;
                          ctx->ri_buf = (int*)plprims; }
                  T_VECTOR
                        { plprims += pl_no_prims*3; }
                  INTEGER
                        { ctx->read_integer = pl_no_prims;
                          ctx->ri_buf = (int*)plmtls; }
                  T_VECTOR
                        { plmtls += pl_no_prims; }
                | '[' pl_tri_ascindex ']'
                ;

pl_tri_ascindex :
                | pl_tri_ascindex T_INTEGER
                        { if (tl_nind == 4 && !(tl_ind++ & 3))
                                *plmtls++ = $2;
                          else
                                *plprims++ = $2; }
                ;

pl_specs        :
                | pl_spec pl_specs
                ;

tex_dims        :
                | tex_dims T_INTEGER
                        { plinfo.line_size += $2;
                          pl_texo[plinfo.no_textures] = $2;
                          plinfo.no_textures++; }
                ;

us_dims         :
                | us_dims T_INTEGER
                        { plinfo.line_size += $2;
                          pl_uso[plinfo.no_users] = $2;
                          plinfo.no_users++; }
                ;

pl_spec         : N
                        { plinfo.normal_offset = plinfo.line_size;
                          plinfo.line_size += 3; }
                | D
                        { plinfo.derivs_offset = plinfo.line_size;
                          plinfo.line_size += 6; }
                | D2
                        { plinfo.derivs2_offset = plinfo.line_size;
                          plinfo.line_size += 9; }
                | M opt_size
                        { plinfo.motion_offset = plinfo.line_size;
                          plinfo.no_motions = $2;
                          plinfo.line_size += $2 * 3; }
                | B opt_size
                        { plinfo.bump_offset = plinfo.line_size;
                          plinfo.no_bumps = $2;
                          plinfo.line_size += $2 * 3; }
                | T_ 
                        { plinfo.texture_offset = plinfo.line_size; }
                  tex_dims
                | U_
                        { plinfo.user_offset = plinfo.line_size; }
                  us_dims
                ;

/* trilists 3.3 */

tl_vectors      :
                | tl_vectors vector
                        { if (tlvec_idx < tl_nvec)
                                tlvec[tlvec_idx++] = $2; }
                ;

tl_vertices     :
                | tl_vertices T_INTEGER
                        { if (tlvert_idx < tl_nvert)
                                tlvert[tlvert_idx++] = $2; }
                ;

tl_triangles    : symbol T_INTEGER T_INTEGER T_INTEGER
                        { tl_indbuf[0] = $2; tl_indbuf[1] = $3;
                          tl_indbuf[2] = $4;
                          mi_api_trilist_triangle($1, tl_indbuf); }
                  tl_tri_mtl
                | tl_tri_index
                ;

tl_tri_mtl      :
                | tl_tri_mtl opt_symbol T_INTEGER T_INTEGER T_INTEGER
                        { tl_indbuf[0] = $3; tl_indbuf[1] = $4;
                          tl_indbuf[2] = $5;
                                mi_api_trilist_triangle($2, tl_indbuf); }
                ;

tl_tri_index    :
                | tl_tri_index T_INTEGER
                        { tl_indbuf[tl_ind++] = $2;
                          if (tl_ind == tl_nind) {
                                mi_api_trilist_triangles(tl_indbuf, 1);
                                tl_ind = 0;
                          }}
                ;

tl_specs        :
                | tl_spec tl_specs
                ;

tl_spec         : N
                        { tlcont.normal_offset = tlcont.sizeof_vertex;
                          tlcont.sizeof_vertex++; }
                | D
                        { tlcont.derivs_offset = tlcont.sizeof_vertex;
                          tlcont.sizeof_vertex++; }
                | D2
                        { tlcont.derivs2_offset = tlcont.sizeof_vertex;
                          tlcont.sizeof_vertex++; }
                | M opt_size
                        { tlcont.motion_offset = tlcont.sizeof_vertex;
                          tlcont.no_motions = $2;
                          tlcont.sizeof_vertex += $2; }
                | T_ opt_size
                        { tlcont.texture_offset = tlcont.sizeof_vertex;
                          tlcont.no_textures = $2;
                          tlcont.sizeof_vertex += $2; }
                | B opt_size
                        { tlcont.bump_offset = tlcont.sizeof_vertex;
                          tlcont.no_bumps = $2;
                          tlcont.sizeof_vertex += $2; }
                | U_ opt_size
                        { tlcont.user_offset = tlcont.sizeof_vertex;
                          tlcont.no_users = $2;
                          tlcont.sizeof_vertex += $2; }
                ;

opt_size        :
                        { $$ = 1; }
                | T_INTEGER
                        { $$ = $1; }
                ;

tl_approx       :
                | approximation
                ;

 isect_object   : INTERSECTION function
                        { curr_obj->type = miOBJECT_INTERSECT_FUNC;
                          curr_obj->geo.intersect_func = $2; }
                ;


/*-----------------------------------------------------------------------------
 * approximations (in objects and options)
 *---------------------------------------------------------------------------*/

approximation   :       { miAPPROX_DEFAULT(approx); }
                  approx_flags approx_body
                ;

approx_flags    :
                | approx_flag approx_flags
                ;

approx_flag     : VISIBLE
                        { approx.flag |= miAPPROX_FLAG_VISIBLE; }
                | TRACE
                        { approx.flag |= miAPPROX_FLAG_TRACE; }
                | SHADOW
                        { approx.flag |= miAPPROX_FLAG_SHADOW; }
                | CAUSTIC
                        { approx.flag |= miAPPROX_FLAG_CAUSTIC; }
                | GLOBILLUM
                        { approx.flag |= miAPPROX_FLAG_GLOBILLUM; }
                ;

approx_body     : APPROXIMATE SURFACE  s_approx_tech s_approx_names
                | APPROXIMATE SUBDIVISION SURFACE
                                       c_approx_tech sds_approx_names
                | APPROXIMATE CCMESH
                                       c_approx_tech ccm_approx_names
                | APPROXIMATE DISPLACE s_approx_tech d_approx_names
                | APPROXIMATE CURVE    c_approx_tech c_approx_names
                | APPROXIMATE SPACE CURVE
                                       c_approx_tech spc_approx_names
                | APPROXIMATE TRIM     c_approx_tech t_approx_names
                | APPROXIMATE          s_approx_tech
                        { mi_api_poly_approx(&approx); }
                | APPROXIMATE TRILIST s_approx_tech
                        { mi_api_trilist_approx(&approx); }
                ;

s_approx_tech   : s_approx_params
                        { approx.subdiv[miMIN]  = 0;
                          approx.subdiv[miMAX]  = 5;
                          approx.max            = miHUGE_INT;
                          if (approx.style == miAPPROX_STYLE_FINE ||
                              approx.style == miAPPROX_STYLE_FINE_NO_SMOOTHING)
                                approx.subdiv[miMAX] = 7; }
                | s_approx_params T_INTEGER T_INTEGER
                        { approx.subdiv[miMIN]  = $2;
                          approx.subdiv[miMAX]  = $3;
                          approx.max            = miHUGE_INT; }
                | s_approx_params MAX_ T_INTEGER
                        { approx.subdiv[miMIN]  = 0;
                          approx.subdiv[miMAX]  = 5;
                          approx.max            = $3;
                          if (approx.style == miAPPROX_STYLE_FINE ||
                              approx.style == miAPPROX_STYLE_FINE_NO_SMOOTHING)
                                approx.subdiv[miMAX] = 7; }
                | s_approx_params T_INTEGER T_INTEGER MAX_ T_INTEGER
                        { approx.subdiv[miMIN]  = $2;
                          approx.subdiv[miMAX]  = $3;
                          approx.max            = $5; }
                | s_approx_params SAMPLES T_INTEGER
                        { approx.subdiv[miMIN]  = 0;
                          approx.subdiv[miMAX]  = 5;
                          approx.max            = $3;
                          if (approx.style == miAPPROX_STYLE_FINE ||
                              approx.style == miAPPROX_STYLE_FINE_NO_SMOOTHING)
                                approx.subdiv[miMAX] = 7; }
                | s_approx_params T_INTEGER T_INTEGER SAMPLES T_INTEGER
                        { approx.subdiv[miMIN]  = $2;
                          approx.subdiv[miMAX]  = $3;
                          approx.max            = $5; }
                ;

c_approx_tech   : c_approx_params
                        { approx.subdiv[miMIN]  = 0;
                          approx.subdiv[miMAX]  = 5; }
                | c_approx_params T_INTEGER T_INTEGER
                        { approx.subdiv[miMIN]  = $2;
                          approx.subdiv[miMAX]  = $3; }
                ;

s_approx_params : s_approx_param
                | s_approx_param s_approx_params
                ;

c_approx_params : c_approx_param
                | c_approx_param c_approx_params
                ;

s_approx_param  : x_approx_param
                | PARAMETRIC floating floating
                        { approx.method                 = miAPPROX_PARAMETRIC;
                          approx.cnst[miCNST_UPARAM]    = $2;
                          approx.cnst[miCNST_VPARAM]    = $3; }
                | REGULAR PARAMETRIC floating floating
                        { approx.method                 = miAPPROX_REGULAR;
                          approx.cnst[miCNST_UPARAM]    = $3;
                          approx.cnst[miCNST_VPARAM]    = $4; }
                | REGULAR PARAMETRIC floating '%' floating '%'
                        { approx.method             = miAPPROX_REGULAR_PERCENT;
                          approx.cnst[miCNST_UPARAM]    = $3;
                          approx.cnst[miCNST_VPARAM]    = $5; }
                | IMPLICIT
                        { approx.method                 = miAPPROX_ALGEBRAIC; }
                ;

c_approx_param  : x_approx_param
                | PARAMETRIC floating
                        { approx.method                 = miAPPROX_PARAMETRIC;
                          approx.cnst[miCNST_UPARAM]    = $2;
                          approx.cnst[miCNST_VPARAM]    = 1.0; }
                | REGULAR PARAMETRIC floating
                        { approx.method                 = miAPPROX_REGULAR;
                          approx.cnst[miCNST_UPARAM]    = $3;
                          approx.cnst[miCNST_VPARAM]    = 1.0; }
                | REGULAR PARAMETRIC floating '%'
                        { approx.method            = miAPPROX_REGULAR_PERCENT;
                          approx.cnst[miCNST_UPARAM]    = $3;
                          approx.cnst[miCNST_VPARAM]    = 100.0; }
                ;

x_approx_param  : VIEW
                        { approx.view_dep      |= 1; }
                | OFFSCREEN
                        { approx.view_dep      |= 2; }
                | ANY
                        { approx.any            = miTRUE; }
                | TREE
                        { approx.style          = miAPPROX_STYLE_TREE; }
                | GRID
                        { approx.style          = miAPPROX_STYLE_GRID; }
                | DELAUNAY
                        { approx.style          = miAPPROX_STYLE_DELAUNAY; }
                | FINE
                        { approx.style          = miAPPROX_STYLE_FINE; }
                | FINE NOSMOOTHING
                        { approx.style = miAPPROX_STYLE_FINE_NO_SMOOTHING; }
                | SHARP floating
                        { approx.sharp          = $2<0 ? 0   : 
                                                  $2>1 ? 255 : 
                                                       (miUint1)($2*255.);}
                | LENGTH floating
                        { approx.method         = miAPPROX_LDA;
                          approx.cnst[miCNST_LENGTH]    = $2; }
                | DISTANCE floating
                        { approx.method                 = miAPPROX_LDA;
                          approx.cnst[miCNST_DISTANCE]  = $2; }
                | ANGLE floating
                        { approx.method                 = miAPPROX_LDA;
                          approx.cnst[miCNST_ANGLE]     = $2; }
                | SPATIAL approx_view floating
                        { approx.method                 = miAPPROX_SPATIAL;
                          approx.cnst[miCNST_LENGTH]    = $3; }
                | CURVATURE approx_view floating floating
                        { approx.method                 = miAPPROX_CURVATURE;
                          approx.cnst[miCNST_DISTANCE]  = $3;
                          approx.cnst[miCNST_ANGLE]     = $4; }
                | GRADING floating
                        { approx.grading                = $2; }
                ;

approx_view     :
                | VIEW
                        { approx.view_dep              |= 1; }
                | OFFSCREEN
                        { approx.view_dep              |= 2; }
                ;

s_approx_names  : symbol
                        { mi_api_surface_approx($1, &approx); }
                | s_approx_names symbol
                        { mi_api_surface_approx($2, &approx); }
                ;

sds_approx_names: symbol
                        { mi_api_subdivsurf_approx($1, &approx); }
                | sds_approx_names symbol
                        { mi_api_subdivsurf_approx($2, &approx); }
                ;

ccm_approx_names: symbol
                        { mi_api_ccmesh_approx($1, &approx); }
                | ccm_approx_names symbol
                        { mi_api_ccmesh_approx($2, &approx); }
                ;

d_approx_names  : symbol
                        { mi_api_surface_approx_displace($1, &approx); }
                | s_approx_names symbol
                        { mi_api_surface_approx_displace($2, &approx); }
                ;

c_approx_names  : symbol
                        { mi_api_curve_approx($1, &approx); }
                | c_approx_names symbol
                        { mi_api_curve_approx($2, &approx); }
                ;

spc_approx_names: symbol
                        { mi_api_spacecurve_approx($1, &approx); }
                | c_approx_names symbol
                        { mi_api_spacecurve_approx($2, &approx); }
                ;

t_approx_names  : symbol
                        { mi_api_surface_approx_trim($1, &approx); }
                | t_approx_names symbol
                        { mi_api_surface_approx_trim($2, &approx); }
                ;

                                                          /* smallparser_end */


/*-----------------------------------------------------------------------------
 * Reality Server and Reality Designer compatibility
 *---------------------------------------------------------------------------*/

options_attribute
                : ATTRIBUTE opt_override options_attribute_item
                /* for parsing of Reality Server and Reality Designer scenes */
                | ATTRIBUTE opt_override attr_flag
                | AMBIENTOCCLUSION boolean
                | AMBIENTOCCLUSION REBUILD boolean
                | AMBIENTOCCLUSION REBUILD FREEZE
                | AMBIENTOCCLUSION FILTER filter_type
                | AMBIENTOCCLUSION FILTER filter_type floating
                | AMBIENTOCCLUSION IMPORTANCE floating
                | AMBIENTOCCLUSION IMPORTANCE floating floating
                | AMBIENTOCCLUSION FALLOFF floating
                | AMBIENTOCCLUSION FALLOFF floating floating
                | AMBIENTOCCLUSION ACCURACY floating
                | AMBIENTOCCLUSION ACCURACY floating floating
                | IBL boolean
                | IBL FALLOFF floating
                | IBL FALLOFF floating floating
                | IBL ACCURACY floating
                | IBL ACCURACY floating floating
                | IBL JITTER boolean
                | FINALGATHER IMPORTANCE floating
                | FINALGATHER IMPORTANCE floating floating
                | TRACE IMPORTANCE floating
                | TRACE IMPORTANCE floating floating
                | TRACE FALLOFF floating
                | TRACE FALLOFF floating floating
                | GLOBILLUM IMPORTANCE floating
                | GLOBILLUM IMPORTANCE floating floating
                | GLOBILLUM FALLOFF floating
                | GLOBILLUM FALLOFF floating floating
                | CAUSTIC IMPORTANCE floating
                | CAUSTIC IMPORTANCE floating floating
                | CAUSTIC FALLOFF floating
                | CAUSTIC FALLOFF floating floating
                ;

options_attribute_item  
                : decl_modifiers BOOLEAN T_STRING boolean 
                        { string_options->set($3, $4 != 0); 
                          mi_api_release($3); }
                | decl_modifiers INTEGER T_STRING T_INTEGER
                        { string_options->set($3, $4);
                          mi_api_release($3); }
                | decl_modifiers SCALAR T_STRING floating
                        { string_options->set($3, (float)$4);
                          mi_api_release($3); }  
                | decl_modifiers COLOR T_STRING floating floating floating floating
                        { string_options->set($3, (float)$4, (float)$5, (float)$6, (float)$7);
                          mi_api_release($3); }
                | decl_modifiers VECTOR T_STRING floating floating floating
                        { string_options->set($3, (float)$4, (float)$5, (float)$6);
                          mi_api_release($3); }
                | decl_modifiers STRING T_STRING T_STRING
                        { string_options->set($3, $4);
                          mi_api_release($3);
                          mi_api_release($4); }  
                ;

dummy_attribute : ATTRIBUTE opt_override dummy_attribute_item
                | ATTRIBUTE opt_override attr_flag
                ;

dummy_attribute_item    
                : decl_modifiers BOOLEAN T_STRING boolean
                        { mi_api_release($3); }
                | decl_modifiers INTEGER T_STRING T_INTEGER
                        { mi_api_release($3); }
                | decl_modifiers SCALAR T_STRING floating
                        { mi_api_release($3); }
                | decl_modifiers COLOR T_STRING floating floating floating floating
                        { mi_api_release($3); }
                | decl_modifiers VECTOR T_STRING floating floating floating
                        { mi_api_release($3); }
                | decl_modifiers STRING T_STRING T_STRING
                        { mi_api_release($3);
                          mi_api_release($4); }
                ;


opt_override    :
                | OVERRIDE
                ;

decl_modifiers  : decl_mod_list
                ;

decl_mod_list   : decl_mod_list CONST_
                | decl_mod_list GLOBAL
                |
                ;

attr_flag       : HIDE boolean
                | VISIBLE boolean
                | TRANSPARENCY T_INTEGER
                | REFLECTION T_INTEGER
                | REFRACTION T_INTEGER
                | SHADOW boolean
                | SHADOW T_INTEGER
                | FINALGATHER boolean
                | FINALGATHER T_INTEGER
                | CAUSTIC boolean
                | CAUSTIC T_INTEGER
                | GLOBILLUM boolean
                | GLOBILLUM T_INTEGER
                | MOTION boolean
                | FACE FRONT
                | FACE BACK
                | FACE BOTH
                | SELECT boolean
                | HULL boolean
                | SHADOWMAP boolean
                | TRACE boolean
                | CAUSTIC
                | GLOBILLUM
                | FINALGATHER
                | HARDWARE
                | HARDWARE boolean
                | TAG T_INTEGER
                ;


/*-----------------------------------------------------------------------------
 * user-interface commands
 *---------------------------------------------------------------------------*/

gui             : GUI opt_symbol
                        { mi_api_gui_begin($2); }
                  '(' gui_attr_list ')' '{' gui_controls '}'
                        { mi_api_gui_end(); }
                | GUI opt_symbol
                        { mi_api_gui_begin($2); }
                  '{' gui_controls '}'
                        { mi_api_gui_end(); }
                ;

gui_elems       :
                | gui_elem gui_elems
                ;

gui_elem        : '(' gui_attr_list ')'
                | '{'
                        { mi_api_gui_push(); }
                  gui_controls '}'
                        { mi_api_gui_pop(); }
                ;

gui_controls    :
                | gui_control gui_controls
                ;

gui_control     : CONTROL symbol opt_symbol
                        { mi_api_gui_control_begin($3?$2:0, $3?$3:$2); }
                  gui_elems
                        { mi_api_gui_control_end(); }
                ;

gui_attr_list   :
                | ','
                | gui_attr
                | gui_attr ',' gui_attr_list
                ;

gui_attr        : symbol
                        { mi_api_gui_attr($1, miNTYPES, 0); }
                | symbol boolean
                        { mi_api_gui_attr($1, miTYPE_BOOLEAN, 1, $2); }
                | symbol floating
                        { mi_api_gui_attr($1, miTYPE_SCALAR, 1, $2); }
                | symbol floating floating
                        { mi_api_gui_attr($1, miTYPE_SCALAR, 2, $2, $3); }
                | symbol floating floating floating
                        { mi_api_gui_attr($1, miTYPE_SCALAR, 3, $2, $3, $4); }
                | symbol floating floating floating floating
                        { mi_api_gui_attr($1, miTYPE_SCALAR, 4, $2,$3,$4,$5); }
                | symbol symbol
                        { mi_api_gui_attr($1, miTYPE_STRING, 1, $2); }
                ;

