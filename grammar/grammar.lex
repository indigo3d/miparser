/*
  GNU's Flex scanner for a mi file shader declarations
  
//  Copyright (c) 2004, Gonzalo Garramuno
//
//  All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//  *       Redistributions of source code must retain the above copyright
//  notice, this list of conditions and the following disclaimer.
//  *       Redistributions in binary form must reproduce the above
//  copyright notice, this list of conditions and the following disclaimer
//  in the documentation and/or other materials provided with the
//  distribution.
//  *       Neither the name of Gonzalo Garramuno nor the names of
//  its other contributors may be used to endorse or promote products derived
//  from this software without specific prior written permission. 
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
//  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
//  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
//  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
//  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
//  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
//  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
//  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
//  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
//   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
//  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//

 */

%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

struct mrShaderParameter;
#include "fileobjgrammar.hpp"

extern YYSTYPE yylval;


struct INCLUDE_STACK
{
     YY_BUFFER_STATE buf;
     char* file;
     unsigned line;
};

 
#ifdef WIN32
#define READ_MODE "rb"
#else
#define READ_MODE "r"
#endif
 

#define MAX_INCLUDE_DEPTH 11
 struct INCLUDE_STACK include_stack[MAX_INCLUDE_DEPTH];
 static int include_stack_ptr = -1;
 static int string_caller;

 char* yyfile = NULL;
 unsigned yyline = 1;
 
#define YYERROR_VERBOSE 1
#define YY_DEBUG 0


 unsigned reserve_strings = 1024;
 unsigned max_strings = 0;
 unsigned num_strings = 0;
 char** string_elem = NULL;
 
 
 int new_file( const char* text, int len );
 int next_file();
 
 extern void yyerror(const char *str);


#if YY_DEBUG
#define DBG(fmt,var) fprintf(stderr, fmt, var);
#if YY_DEBUG > 1
#define DBG_TOKEN() fprintf(stderr,"grammar.lex: Matched rule: %d\n", __LINE__);
#else
#define DBG_TOKEN()
#endif
#else
#define DBG(fmt,var)
#define DBG_TOKEN()
#endif
 
 void free_all_strings();
 char* new_string( const char* s );
 
int yywrap()
{
   free_all_strings();
   return 1;
} 
%}

DIGIT      [0-9]                 
WORD       [A-Za-z0-9_]+
string     \"[^\n\"]+\"

%s NODEID INCLUDE LOOKUP 
%s STR MULTILINESTR BINVEC MAYA HELPMSG

%option never-interactive

%%
<INITIAL>"lightprofile"	{ DBG_TOKEN(); return LIGHTPROFILE; }
<INITIAL>"acceleration"	{ DBG_TOKEN(); return ACCELERATION; }
<INITIAL>"subdivision"	{ DBG_TOKEN(); return SUBDIVISION; }
<INITIAL>"premultiply"	{ DBG_TOKEN(); return PREMULTIPLY; }
<INITIAL>"inheritance"	{ DBG_TOKEN(); return INHERITANCE; }
<INITIAL>"incremental"	{ DBG_TOKEN(); return INCREMENTAL; }
<INITIAL>"finalgather"	{ DBG_TOKEN(); return FINALGATHER; }
<INITIAL>"environment"	{ DBG_TOKEN(); return ENVIRONMENT; }
<INITIAL>"approximate"	{ DBG_TOKEN(); return APPROXIMATE; }
<INITIAL>"samplelock"	{ DBG_TOKEN(); return SAMPLELOCK; }
<INITIAL>"resolution"	{ DBG_TOKEN(); return RESOLUTION; }
<INITIAL>"phenomenon"	{ DBG_TOKEN(); return PHENOMENON; }
<INITIAL>"parametric"	{ DBG_TOKEN(); return PARAMETRIC; }
<INITIAL>"irradiance"	{ DBG_TOKEN(); return IRRADIANCE; }
<INITIAL>"interface"	{ DBG_TOKEN(); return INTERFACE_; }
<INITIAL>"diagnostic"	{ DBG_TOKEN(); return DIAGNOSTIC; }
<INITIAL>"desaturate"	{ DBG_TOKEN(); return DESATURATE; }
<INITIAL>"derivative"	{ DBG_TOKEN(); return DERIVATIVE; }
<INITIAL>"autovolume"   { DBG_TOKEN(); return AUTOVOLUME; } 
<INITIAL>"transform"	{ DBG_TOKEN(); return TRANSFORM; }
<INITIAL>"shadowmap"	{ DBG_TOKEN(); return SHADOWMAP; }
<INITIAL>"recursive"	{ DBG_TOKEN(); return RECURSIVE; }
<INITIAL>"rectangle"	{ DBG_TOKEN(); return RECTANGLE; }
<INITIAL>"photonvol"	{ DBG_TOKEN(); return PHOTONVOL; }
<INITIAL>"photonmap"	{ DBG_TOKEN(); return PHOTONMAP; }
<INITIAL>"parallel"	{ DBG_TOKEN(); return PARALLEL_; }
<INITIAL>"nocontour"	{ DBG_TOKEN(); return NOCONTOUR; }
<INITIAL>"namespace"	{ DBG_TOKEN(); return NAMESPACE; }
<INITIAL>"instgroup"	{ DBG_TOKEN(); return INSTGROUP; }
<INITIAL>"infinity"	{ DBG_TOKEN(); return INFINITY_; }
<INITIAL>"globillum"	{ DBG_TOKEN(); return GLOBILLUM; }
<INITIAL>"direction"	{ DBG_TOKEN(); return DIRECTION; }
<INITIAL>"curvature"	{ DBG_TOKEN(); return CURVATURE; }
<INITIAL>"colorclip"	{ DBG_TOKEN(); return COLORCLIP; }
<INITIAL>"triangle"	{ DBG_TOKEN(); return TRIANGLE; }
<INITIAL>"softness"	{ DBG_TOKEN(); return SOFTNESS; }
<INITIAL>"segments"	{ DBG_TOKEN(); return SEGMENTS; }
<INITIAL>"scanline"	{ DBG_TOKEN(); return SCANLINE; }
<INITIAL>"registry"	{ DBG_TOKEN(); return REGISTRY; }
<INITIAL>"rational"	{ DBG_TOKEN(); return RATIONAL; }
<INITIAL>"priority"	{ DBG_TOKEN(); return PRIORITY; }
<INITIAL>"mitchell"	{ DBG_TOKEN(); return MITCHELL; }
<INITIAL>"material"	{ DBG_TOKEN(); return MATERIAL; }
<INITIAL>"lightmap"	{ DBG_TOKEN(); return LIGHTMAP; }
<INITIAL>"instance"	{ DBG_TOKEN(); return INSTANCE; }
<INITIAL>"implicit"	{ DBG_TOKEN(); return IMPLICIT; }
<INITIAL>"geometry"	{ DBG_TOKEN(); return GEOMETRY; }
<INITIAL>"exponent"	{ DBG_TOKEN(); return EXPONENT; }
<INITIAL>"distance"	{ DBG_TOKEN(); return DISTANCE; }
<INITIAL>"displace"	{ DBG_TOKEN(); return DISPLACE; }
<INITIAL>"delaunay"	{ DBG_TOKEN(); return DELAUNAY; }
<INITIAL>"cylinder"	{ DBG_TOKEN(); return CYLINDER; }
<INITIAL>"contrast"	{ DBG_TOKEN(); return CONTRAST; }
<INITIAL>"constant"	{ DBG_TOKEN(); return CONSTANT; }
<INITIAL>"cardinal"	{ DBG_TOKEN(); return CARDINAL; }
<INITIAL>"boolean"	{ DBG_TOKEN(); return BOOLEAN_; }
<INITIAL>"aperture"	{ DBG_TOKEN(); return APERTURE; }
<INITIAL>"adaptive"	{ DBG_TOKEN(); return ADAPTIVE; }
<INITIAL>"accuracy"	{ DBG_TOKEN(); return ACCURACY; }
<INITIAL>"visible"	{ DBG_TOKEN(); return VISIBLE; }
<INITIAL>"version"	{ DBG_TOKEN(); return VERSION; }
<INITIAL>"verbose"	{ DBG_TOKEN(); return VERBOSE; }
<INITIAL>"texture"	{ DBG_TOKEN(); return TEXTURE; }
<INITIAL>"surface"	{ DBG_TOKEN(); return SURFACE; }
<INITIAL>"special"	{ DBG_TOKEN(); return SPECIAL; }
<INITIAL>"spatial"	{ DBG_TOKEN(); return SPATIAL; }
<INITIAL>"shutter"	{ DBG_TOKEN(); return SHUTTER; }
<INITIAL>"samples"	{ DBG_TOKEN(); return SAMPLES; }
<INITIAL>"regular"	{ DBG_TOKEN(); return REGULAR; }
<INITIAL>"rebuild"	{ DBG_TOKEN(); return REBUILD; }
<INITIAL>"quality"	{ DBG_TOKEN(); return QUALITY; }
<INITIAL>"polygon"	{ DBG_TOKEN(); return POLYGON; }
<INITIAL>"photons"	{ DBG_TOKEN(); return PHOTONS; }
<INITIAL>"options"	{ DBG_TOKEN(); return OPTIONS; }
<INITIAL>"opaque"	{ DBG_TOKEN(); return OPAQUE_; }
<INITIAL>"lanczos"	{ DBG_TOKEN(); return LANCZOS; }
<INITIAL>"integer"	{ DBG_TOKEN(); return INTEGER; }
<INITIAL>"grading"	{ DBG_TOKEN(); return GRADING; }
<INITIAL>"emitter"	{ DBG_TOKEN(); return EMITTER; }
<INITIAL>"density"	{ DBG_TOKEN(); return DENSITY; }
<INITIAL>"delete"	{ DBG_TOKEN(); return DELETE_; }
<INITIAL,MAYA>"default"	{ DBG_TOKEN(); return DEFAULT; }
<INITIAL>"declare"	{ DBG_TOKEN(); return DECLARE; }
<INITIAL>"control"	{ DBG_TOKEN(); return CONTROL; }
<INITIAL>"contour"	{ DBG_TOKEN(); return CONTOUR; }
<INITIAL>"connect"	{ DBG_TOKEN(); return CONNECT; }
<INITIAL>"caustic"	{ DBG_TOKEN(); return CAUSTIC; }
<INITIAL>"bspline"	{ DBG_TOKEN(); return BSPLINE; }
<INITIAL>"window"	{ DBG_TOKEN(); return WINDOW; }
<INITIAL>"volume"	{ DBG_TOKEN(); return VOLUME; }
<INITIAL>"vertex"       { DBG_TOKEN(); return VERTEX; }
<INITIAL>"vector"	{ DBG_TOKEN(); return VECTOR; }
<INITIAL>"taylor"	{ DBG_TOKEN(); return TAYLOR; }
<INITIAL>"tagged"	{ DBG_TOKEN(); return TAGGED; }
<INITIAL>"system"	{ DBG_TOKEN(); return SYSTEM; }
<INITIAL>"struct"	{ DBG_TOKEN(); return STRUCT; }
<INITIAL>"string"	{ DBG_TOKEN(); return STRING; }
<INITIAL>"spread"	{ DBG_TOKEN(); return SPREAD; }
<INITIAL>"sphere"	{ DBG_TOKEN(); return SPHERE; }
<INITIAL>"shadow"	{ DBG_TOKEN(); return SHADOW; }
<INITIAL>"shader"	{ DBG_TOKEN(); return SHADER; }
<INITIAL>"scalar"	{ DBG_TOKEN(); return SCALAR; }
<INITIAL>"render"	{ DBG_TOKEN(); return RENDER; }
<INITIAL>"photon"	{ DBG_TOKEN(); return PHOTON; }
<INITIAL>"output"	{ DBG_TOKEN(); return OUTPUT; }
<INITIAL>"origin"	{ DBG_TOKEN(); return ORIGIN; }
<INITIAL>"opengl"	{ DBG_TOKEN(); return OPENGL; }
<INITIAL>"offset"	{ DBG_TOKEN(); return OFFSET; }
<INITIAL>"object"	{ DBG_TOKEN(); return OBJECT; }
<INITIAL>"motion"	{ DBG_TOKEN(); return MOTION; }
<INITIAL>"memory"	{ DBG_TOKEN(); return MEMORY; }
<INITIAL>"matrix"	{ DBG_TOKEN(); return MATRIX; }
<INITIAL>"mapsto"	{ DBG_TOKEN(); return MAPSTO; }
<INITIAL>"length"	{ DBG_TOKEN(); return LENGTH; }
<INITIAL>"jitter"	{ DBG_TOKEN(); return JITTER; }
<INITIAL>"filter"	{ DBG_TOKEN(); return FILTER; }
<INITIAL>"false"	{ DBG_TOKEN(); return FALSE_; }
<INITIAL>"energy"	{ DBG_TOKEN(); return ENERGY; }
<INITIAL>"dither"	{ DBG_TOKEN(); return DITHER; }
<INITIAL>"debug"	{ DBG_TOKEN(); return DEBUG_; }
<INITIAL>"crease"	{ DBG_TOKEN(); return CREASE; }
<INITIAL>"corner"	{ DBG_TOKEN(); return CORNER; }
<INITIAL>"camera"	{ DBG_TOKEN(); return CAMERA; }
<INITIAL>"buffer"	{ DBG_TOKEN(); return BUFFER; }
<INITIAL>"bezier"	{ DBG_TOKEN(); return BEZIER; }
<INITIAL>"aspect"	{ DBG_TOKEN(); return ASPECT; }
<INITIAL>"world"	{ DBG_TOKEN(); return WORLD; }
<INITIAL>"width"	{ DBG_TOKEN(); return WIDTH; }
<INITIAL>"white"	{ DBG_TOKEN(); return WHITE; }
<INITIAL>"value"	{ DBG_TOKEN(); return VALUE; }
<INITIAL>"true"	{ DBG_TOKEN(); return TRUE_; }
<INITIAL>"trace"	{ DBG_TOKEN(); return TRACE; }
<INITIAL>"strip"	{ DBG_TOKEN(); return STRIP; }
<INITIAL>"store"	{ DBG_TOKEN(); return STORE; }
<INITIAL>"state"	{ DBG_TOKEN(); return STATE; }
<INITIAL>"space"	{ DBG_TOKEN(); return SPACE; }
<INITIAL>"smart"	{ DBG_TOKEN(); return SMART; }
<INITIAL>"size"	{ DBG_TOKEN(); return SIZE_; }
<INITIAL>"raycl"	{ DBG_TOKEN(); return RAYCL; }
<INITIAL>"null"	{ DBG_TOKEN(); return NULL_; }
<INITIAL>"mixed"	{ DBG_TOKEN(); return MIXED; }
<INITIAL>"merge"	{ DBG_TOKEN(); return MERGE; }
<INITIAL>"local"	{ DBG_TOKEN(); return LOCAL; }
<INITIAL>"light"	{ DBG_TOKEN(); return LIGHT; }
<INITIAL>"group"	{ DBG_TOKEN(); return GROUP; }
<INITIAL>"green"	{ DBG_TOKEN(); return GREEN; }
<INITIAL>"gauss"	{ DBG_TOKEN(); return GAUSS; }
<INITIAL>"gamma"	{ DBG_TOKEN(); return GAMMA; }
<INITIAL>"front"	{ DBG_TOKEN(); return FRONT; }
<INITIAL>"frame"	{ DBG_TOKEN(); return FRAME; }
<INITIAL>"focal"	{ DBG_TOKEN(); return FOCAL; }
<INITIAL>"file"	{ DBG_TOKEN(); return FILE_; }
<INITIAL>"field"	{ DBG_TOKEN(); return FIELD; }
<INITIAL>"depth"	{ DBG_TOKEN(); return DEPTH; }
<INITIAL>"curve"	{ DBG_TOKEN(); return CURVE; }
<INITIAL>"conic"	{ DBG_TOKEN(); return CONIC; }
<INITIAL>"color"	{ DBG_TOKEN(); return COLOR; }
<INITIAL>"basis"	{ DBG_TOKEN(); return BASIS; }
<INITIAL>"array"	{ DBG_TOKEN(); return ARRAY; }
<INITIAL>"apply"	{ DBG_TOKEN(); return APPLY; }
<INITIAL>"angle"	{ DBG_TOKEN(); return ANGLE; }
<INITIAL>"alpha"	{ DBG_TOKEN(); return ALPHA; }
<INITIAL>"view"	{ DBG_TOKEN(); return VIEW; }
<INITIAL>"trim"	{ DBG_TOKEN(); return TRIM; }
<INITIAL>"tree"	{ DBG_TOKEN(); return TREE; }
<INITIAL>"time"	{ DBG_TOKEN(); return TIME; }
<INITIAL>"task"	{ DBG_TOKEN(); return TASK; }
<INITIAL>"spdl"	{ DBG_TOKEN(); return SPDL; }
<INITIAL>"sort"	{ DBG_TOKEN(); return SORT; }
<INITIAL>"root"	{ DBG_TOKEN(); return ROOT; }
<INITIAL>"rgb"	{ DBG_TOKEN(); return RGB_; }
<INITIAL,MAYA>"min"	{ DBG_TOKEN(); return MIN_; }
<INITIAL,MAYA>"max"	{ DBG_TOKEN(); return MAX_; }
<INITIAL>"link"	{ DBG_TOKEN(); return LINK; }
<INITIAL>"lens"	{ DBG_TOKEN(); return LENS; }
<INITIAL>"hole"	{ DBG_TOKEN(); return HOLE; }
<INITIAL>"hide"	{ DBG_TOKEN(); return HIDE; }
<INITIAL>"grid"	{ DBG_TOKEN(); return GRID; }
<INITIAL>"face"	{ DBG_TOKEN(); return FACE; }
<INITIAL>"even"	{ DBG_TOKEN(); return EVEN; }
<INITIAL>"echo"	{ DBG_TOKEN(); return ECHO; }
<INITIAL>"disc"	{ DBG_TOKEN(); return DISC; }
<INITIAL>"data"	{ DBG_TOKEN(); return DATA; }
<INITIAL>"dart"	{ DBG_TOKEN(); return DART; }
<INITIAL>"cusp"	{ DBG_TOKEN(); return CUSP; }
<INITIAL>"cone"	{ DBG_TOKEN(); return CONE; }
<INITIAL>"code"	{ DBG_TOKEN(); return CODE; }
<INITIAL>"clip"	{ DBG_TOKEN(); return CLIP; }
<INITIAL>"call"	{ DBG_TOKEN(); return CALL; }
<INITIAL>"bump"	{ DBG_TOKEN(); return BUMP; }
<INITIAL>"both"	{ DBG_TOKEN(); return BOTH; }
<INITIAL>"blue"	{ DBG_TOKEN(); return BLUE; }
<INITIAL>"back"	{ DBG_TOKEN(); return BACK; }
<INITIAL>"tag"	{ DBG_TOKEN(); return TAG; }
<INITIAL>"set"	{ DBG_TOKEN(); return SET; }
<INITIAL>"red"	{ DBG_TOKEN(); return RED; }
<INITIAL>"ray"	{ DBG_TOKEN(); return RAY; }
<INITIAL>"raw"	{ DBG_TOKEN(); return RAW; }
<INITIAL>"off"	{ DBG_TOKEN(); return OFF; }
<INITIAL>"odd"	{ DBG_TOKEN(); return ODD; }
<INITIAL>"imp"	{ DBG_TOKEN(); return IMP; }
<INITIAL>"gui"	{ DBG_TOKEN(); return GUI; }
<INITIAL>"fan"	{ DBG_TOKEN(); return FAN; }
<INITIAL>"end"	{ DBG_TOKEN(); return END; }
<INITIAL>"bsp"	{ DBG_TOKEN(); return BSP; }
<INITIAL>"box"	{ DBG_TOKEN(); return BOX; }
<INITIAL>"any"	{ DBG_TOKEN(); return ANY; }
<INITIAL>"all"	{ DBG_TOKEN(); return ALL; }
<INITIAL>"q"	{ DBG_TOKEN(); return Q_; }
<INITIAL>"on"	{ DBG_TOKEN(); return ON; }
<INITIAL>"n"	{ DBG_TOKEN(); return N_; }
<INITIAL>"mi"	{ DBG_TOKEN(); return MI; }
<INITIAL>"cp"	{ DBG_TOKEN(); return CP; }
<INITIAL>"w"	{ DBG_TOKEN(); return W; }
<INITIAL>"v"	{ DBG_TOKEN(); return V; }
<INITIAL>"u"	{ DBG_TOKEN(); return U; }
<INITIAL>"t"	{ DBG_TOKEN(); return T; }
<INITIAL>"p"	{ DBG_TOKEN(); return P; }
<INITIAL>"m"	{ DBG_TOKEN(); return M; }
<INITIAL>"d"	{ DBG_TOKEN(); return D; }
<INITIAL>"c"	{ DBG_TOKEN(); return C; }


<INITIAL>\=		{ DBG_TOKEN(); return '='; }
<INITIAL>\,		{ DBG_TOKEN(); return ','; }
<INITIAL>\(		{ DBG_TOKEN(); return '('; }
<INITIAL>\)		{ DBG_TOKEN(); return ')'; }
<INITIAL>\{		{ DBG_TOKEN(); return '{'; }
<INITIAL>\}		{ DBG_TOKEN(); return '}'; }
<INITIAL>\[		{ DBG_TOKEN(); return '['; }
<INITIAL>\]		{ DBG_TOKEN(); return ']'; }

<INITIAL>"#":             { BEGIN(MAYA); DBG_TOKEN(); return T_MAYA_OPTION; }
<INITIAL>"#"\n            { DBG_TOKEN(); ++yyline; }
<INITIAL>"#"[^:\n].*\n    { DBG_TOKEN(); ++yyline; }


<INITIAL,MAYA>[+-]?{DIGIT}*"."{DIGIT}*  {
   /* This matches floating point numbers like: 1. and 1.32 */
   yylval.floating = atof(yytext);
   DBG_TOKEN(); return T_FLOAT;
}

<INITIAL,MAYA>[+-]?{DIGIT}+[dDeE][+-]{DIGIT}+   {
   /* This matches floating point numbers like: 1e+42 */
   yylval.floating = atof(yytext); DBG_TOKEN(); return T_FLOAT;
}

<INITIAL,MAYA>[+-]?{DIGIT}+"."{DIGIT}*[dDeE][+-]{DIGIT}+  {
   /* This matches floating point numbers like: 1.32e+42 */
   yylval.floating = atof(yytext); DBG_TOKEN(); return T_FLOAT;
}

<INITIAL,MAYA>[+-]?{DIGIT}+             {
   yylval.integer = atoi(yytext); DBG_TOKEN(); return T_INTEGER;
}


<INITIAL>^$lookup     { BEGIN(LOOKUP); }
<LOOKUP>[ \t]+      /* eat the whitespace */
<LOOKUP>{string}   { /* got the include file name */
   BEGIN(INITIAL);
}

<INITIAL>^$include     { BEGIN(INCLUDE); }
<INCLUDE>[ \t]+      /* eat the whitespace */
<INCLUDE>{string}   { /* got the include file name */
   new_file(  yytext+1, yyleng-2 );
   BEGIN(INITIAL);
}
<<EOF>> {
   BEGIN(INITIAL);
   if ( next_file() == 0 ) {
      yyterminate();
   }
}



<MAYA>"help"      { DBG_TOKEN(); BEGIN(HELPMSG); return HELP; }
<MAYA>"shortname" { DBG_TOKEN(); return SHORTNAME; }
<MAYA>"softmin"   { DBG_TOKEN(); return SOFTMIN; }
<MAYA>"softmax"   { DBG_TOKEN(); return SOFTMAX; }
<MAYA>"icon"      { DBG_TOKEN(); return ICON; }
<MAYA>"classification" { DBG_TOKEN(); return CLASSIFICATION; }
<MAYA>"nodeid"    { BEGIN(NODEID); DBG_TOKEN(); return NODEID_; }
<MAYA>"#".*\n     { DBG_TOKEN(); BEGIN(INITIAL); ++yyline; }
<MAYA>[\t \r]+    { DBG_TOKEN(); }
<MAYA>\n          { DBG_TOKEN();BEGIN(INITIAL); ++yyline; }

<NODEID>{DIGIT}+  { BEGIN(MAYA); yylval.nodeid = atol(yytext); 
                    DBG_TOKEN(); return T_NODEID; }
<NODEID>\n          { DBG_TOKEN(); BEGIN(INITIAL); ++yyline; }
<NODEID>[ \t\r]+    { DBG_TOKEN(); }
<NODEID>.           { yyerror("missing nodeid"); yyterminate(); }




<INITIAL,MAYA>\"         { DBG_TOKEN(); string_caller = YY_START;
                           BEGIN(STR); }
<STR>[^\n\"]+       {
                      DBG("string:%s\n", yytext);
                      DBG_TOKEN(); yylval.string = new_string(yytext);
		      return T_STRING;
                    }
<STR>[\"\n]         { DBG_TOKEN(); BEGIN(string_caller); } 


<HELPMSG>[\t \r\n]+   { ; }
<HELPMSG>\"            {
                        DBG_TOKEN(); string_caller = MAYA;
                        BEGIN(MULTILINESTR); 
                       }
<HELPMSG>.            {
                        yyerror("Missing help message");
                      }

<MULTILINESTR>[^\"\n\r]+ {
                           DBG_TOKEN(); yylval.string = new_string(yytext);
		           return T_STRING;
                         }
<MULTILINESTR>\n[\t #:]+ { DBG_TOKEN(); ++yyline; }
<MULTILINESTR>\r         { DBG_TOKEN(); }
<MULTILINESTR>\"         { DBG_TOKEN(); BEGIN(string_caller); return END_STR; }





<INITIAL>`                { BEGIN(BINVEC); }
<BINVEC>[^`]+             {
                            yylval.byte_string.len = yyleng;
                            yylval.byte_string.bytes = (unsigned char*) yytext;
			    return T_BYTE_STRING;
                          }
<BINVEC>`                 { BEGIN(INITIAL); }




<INITIAL>{WORD}           {
                            DBG("symbol:%s\n", yytext);
                            yylval.symbol = yylval.string = new_string(yytext);
                            DBG_TOKEN(); return T_SYMBOL;
                          }
<INITIAL>[\ \t\r]+   { DBG_TOKEN(); }
<INITIAL>\n          { ++yyline; DBG_TOKEN(); }
<INITIAL>.                    {
                                DBG_TOKEN();
                                yyerror("illegal token");
                                yyterminate();
                              }

%%


char* new_string( const char* s )
{
   if ( num_strings == max_strings )
   {
      char** old_string_elem = string_elem;
      string_elem = (char**) realloc( string_elem,
				      max_strings + reserve_strings );
      if ( string_elem == NULL )
      {
	 fprintf(stderr,"Run out of memory to realloc strings\n");
	 fflush(stderr);
	 return (char*)s;
      }
      
      if ( string_elem != old_string_elem )
      {
	 memcpy( old_string_elem, string_elem, max_strings * sizeof(char*) );
	 free( old_string_elem );
      }
      max_strings += reserve_strings;
   }
   string_elem[num_strings++] = strdup(s);
   return string_elem[num_strings-1];
}



void alloc_all_strings()
{
   num_strings = 0;
   max_strings = reserve_strings;
   string_elem = (char**) malloc( max_strings * sizeof(char*) );
   if ( string_elem == NULL )
   {
      fprintf(stderr,"Run out of memory to malloc strings\n");
      fflush(stderr);
   }
}



void free_all_strings()
{
   while ( num_strings )
   {
      free( string_elem[--num_strings] );
   }
   free( string_elem );
   string_elem = NULL;
}



int mi_open_file( const char* mifile )
{
   yyline = 1;
   free(yyfile);
   yyfile = strdup( mifile );

   yyin = fopen(yyfile, READ_MODE);
   if ( yyin == NULL )
   {
      free(yyfile); yyfile = NULL;
      return 0;
   }

   
   YY_NEW_FILE;
   
   alloc_all_strings();
   DBG("mi_open_file: %s\n", mifile);
   DBG("file descriptor:%d\n", _fileno(yyin) );
   
   include_stack_ptr = 0;
   include_stack[include_stack_ptr].buf = NULL;
   include_stack[include_stack_ptr].file = yyfile;
   return 1;
}



FILE* search_for_include_file( const char* envpath, const char* incfile )
{
   char filename[256];
   char* buf;
   char* path;
   char* last;
   FILE* incyyin = NULL;

   if ( envpath == NULL ) return NULL;
   
   buf = path = last = strdup(envpath);
   for ( ; *path != 0; ++path )
      if ( *path == ';' ) *path = 0;
   
   path = buf;
   last += strlen(envpath);
   while (path < last ) { 
      sprintf( filename, "%s/%s", path, incfile );
      incyyin = fopen( filename, READ_MODE );
      if ( incyyin ) break;
      path += strlen( path ) + 1;
   }
   free(buf);

   fflush(stderr);
   
   return incyyin;
}


int new_file( const char* text, int len )
{
   char* incfile;
   FILE* incyyin;
   if ( include_stack_ptr >= MAX_INCLUDE_DEPTH-1 )
   {
      yyerror( "Includes nested too deeply" );
      next_file(); return 1;
   }
   
   incfile = strdup(text);
   incfile[len] = 0;
   
   incyyin = fopen( incfile, READ_MODE );
   
   if ( ! incyyin )
   {
      const char* envpath = getenv("MI_CUSTOM_SHADER_PATH");
      incyyin = search_for_include_file( envpath, incfile );
      if ( !incyyin )
      {
	 envpath = getenv("MI_RAY_INCPATH");
	 incyyin = search_for_include_file( envpath, incfile );
      }
      
      if ( !incyyin )
      {
	 yyerror( "Include file not found" );
	 next_file();
	 BEGIN(INITIAL); 
	 return 1;
      }
   }

   include_stack[include_stack_ptr].line = yyline;
   include_stack[include_stack_ptr].buf  = YY_CURRENT_BUFFER;

   ++include_stack_ptr;
   include_stack[include_stack_ptr].file = yyfile = incfile;
   
   yyline = 1;
   yyin = incyyin;
   yy_switch_to_buffer( yy_create_buffer( yyin, YY_BUF_SIZE ) );
   return 0;
}



int next_file()
{
   if ( yyin ) fclose( yyin );
   yyin = NULL;
   free(yyfile);
   free_all_strings();
   if ( --include_stack_ptr < 0 )
   {
      yyfile = NULL;
      return 0;
   }
   else
   {
      yyfile = include_stack[include_stack_ptr].file;
      yyline = include_stack[include_stack_ptr].line;
      yy_delete_buffer( YY_CURRENT_BUFFER );
      yy_switch_to_buffer( include_stack[include_stack_ptr].buf );
   }
   return 1;
 }
