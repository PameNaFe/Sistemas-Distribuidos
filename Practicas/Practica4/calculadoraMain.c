#include "calculadora.h"

int main() {
    int num1, num2;
    char operador;

    printf("Ingrese la operacion (por ejemplo, 5 + 3, 6 - 3): ");
    scanf("%d %c %d", &num1, &operador, &num2);

    switch (operador) {
        case '+':
            printf("El resultado de la suma es: %d\n", suma(num1, num2));
            break;
        case '-':
            printf("El resultado de la resta es: %d\n", resta(num1, num2));
            break;
        case '*':
            printf("El resultado de la multiplicacion es: %d\n", multiplicacion(num1, num2));
            break;
        case '/':
            if (num2 == 0) {
                printf("Error: no se puede dividir por cero\n");
            } else {
                printf("El resultado de la division es: %.2f\n", division(num1, num2));
            }
            break;
        default:
            printf("Operador invalido\n");
    }

    return 0;
}
