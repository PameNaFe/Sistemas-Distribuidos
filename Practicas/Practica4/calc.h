/*
 * Please do not edit this file.
 * It was generated using rpcgen.
 */

#ifndef _CALC_H_RPCGEN
#define _CALC_H_RPCGEN

#include <rpc/rpc.h>


#ifdef __cplusplus
extern "C" {
#endif


struct dato {
	int a;
	int b;
};
typedef struct dato dato;

#define CALC_PROG 0x31230000
#define CALC_VERS 1

#if defined(__STDC__) || defined(__cplusplus)
#define suma 1
extern  int * suma_1(dato *, CLIENT *);
extern  int * suma_1_svc(dato *, struct svc_req *);
#define resta 2
extern  int * resta_1(dato *, CLIENT *);
extern  int * resta_1_svc(dato *, struct svc_req *);
#define multiplicacion 3
extern  int * multiplicacion_1(dato *, CLIENT *);
extern  int * multiplicacion_1_svc(dato *, struct svc_req *);
#define division 4
extern  float * division_1(dato *, CLIENT *);
extern  float * division_1_svc(dato *, struct svc_req *);
extern int calc_prog_1_freeresult (SVCXPRT *, xdrproc_t, caddr_t);

#else /* K&R C */
#define suma 1
extern  int * suma_1();
extern  int * suma_1_svc();
#define resta 2
extern  int * resta_1();
extern  int * resta_1_svc();
#define multiplicacion 3
extern  int * multiplicacion_1();
extern  int * multiplicacion_1_svc();
#define division 4
extern  float * division_1();
extern  float * division_1_svc();
extern int calc_prog_1_freeresult ();
#endif /* K&R C */

/* the xdr functions */

#if defined(__STDC__) || defined(__cplusplus)
extern  bool_t xdr_dato (XDR *, dato*);

#else /* K&R C */
extern bool_t xdr_dato ();

#endif /* K&R C */

#ifdef __cplusplus
}
#endif

#endif /* !_CALC_H_RPCGEN */
