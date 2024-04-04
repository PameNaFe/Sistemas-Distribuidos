/*
 * This is sample code generated by rpcgen.
 * These are only templates and you can use them
 * as a guideline for developing your own functions.
 */

#include "calc.h"

int *
suma_1_svc(dato *argp, struct svc_req *rqstp)
{
	static int  result;
		printf("Server response to client...\n");
		printf("parameters: %d, %d\n", argp->a, argp->b);
		result = argp->a + argp->b;
		printf("returning: %d\n", result);
	return &result;
}

int *
resta_1_svc(dato *argp, struct svc_req *rqstp)
{
	static int  result;
		printf("Server response to client...\n");
		printf("parameters: %d, %d\n", argp->a, argp->b);
		result = argp->a - argp->b;
		printf("returning: %d\n", result);
	return &result;
}

int *
multiplicacion_1_svc(dato *argp, struct svc_req *rqstp)
{
	static int  result;
		printf("Server response to client...\n");
		printf("parameters: %d, %d\n", argp->a, argp->b);
		result = argp->a * argp->b;
		printf("returning: %d\n", result);
	return &result;
}

float *
division_1_svc(dato *argp, struct svc_req *rqstp)
{
	static float  result;
		printf("Server response to client...\n");
		printf("parameters: %d, %d\n", argp->a, argp->b);
		result = argp->a / argp->b;
		printf("returning: %f\n", result);
	return &result;
}
