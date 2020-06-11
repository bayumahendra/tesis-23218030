#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
        char ptr[10];
        if(argc>1){
                FILE *fp = fopen(argv[1], "r");
                fgets(ptr, sizeof(ptr), fp);
        }
        else{
                fgets(ptr, sizeof(ptr), stdin);
        }
        printf("%s", ptr);
        if(ptr[0] == 'a') 
        {
                if(ptr[1] == 'f') 
                {
                        if(ptr[2] == 'l') 
                        {
                                if(ptr[3] == '!') 
                                {
                                        abort();
                                }
                                else    printf("%c",ptr[3]);
                        }
                        else    printf("%c",ptr[2]);
                }
                else    printf("%c",ptr[1]);
        }
        else    printf("%c",ptr[0]);
        return 0;
}
