#include <stdio.h>
#include <stdlib.h>
#include <string.h>

    struct PassRecord {
    int studentID;
    char name[50];
    char passType[20];
    char date[15];
    char reason[100];
};

void addRecord();
void viewAllRecords();
void searchRecord();
void deleteRecord();
void showMenu();
int loginSystem();

const char *FILENAME = "pass_records.txt";

int main() {
    printf("===== Welcome to Hostel Pass Monitoring System =====\n");

    if (loginSystem()) {
        printf("\n Login Successful! Welcome, Satyansh.\n");
    } else {
        printf("\n Too many failed attempts! Exiting program.\n");
    }

    return 0;
}

int loginSystem() {
    char username[20], password[20];
    int attempt = 0;

    const char correctUser[] = "warden@upes";
    const char correctPass[] = "satyanshhere";

    while (attempt < 3) {  
        printf("\nLogin Attempt %d of 3\n", attempt + 1);
        printf("Enter Username: ");
        scanf("%s", username);
        printf("Enter Password: ");
        scanf("%s", password);

        if (strcmp(username, correctUser) == 0 && strcmp(password, correctPass) == 0) {
            return 1; 
        } else {
            printf(" Invalid username or password! Try again.\n");
            attempt++;
        }
    }
    return 0;
}