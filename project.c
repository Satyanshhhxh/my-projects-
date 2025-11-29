#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct PassRecord
{
    int studentID;
    char name[50];
    char passType[20];
    char date[15];
    char reason[100];
};

void addRecord(void);
void viewAllRecords(void);
void searchRecord(void);
void deleteRecord(void);
void showMenu(void);
static void flushStdin(void);
int loginSystem();

const char *FILENAME = "pass_records.txt";

int main(void)
{
    printf("===== Welcome to Hostel Pass Monitoring System =====\n");

    if (loginSystem())
    {
        printf("\nLogin Successful! Welcome, Warden.\n");
        showMenu();
    }
    else
    {
        printf("\nToo many failed attempts! Exiting program.\n");
    }

    return 0;
}

int loginSystem(void)
{
    char username[50], password[50];
    int attempt = 0;

    const char correctUser[] = "warden@upes";
    const char correctPass[] = "satyanshhere";

    while (attempt < 3)
    {
        printf("\nLogin Attempt %d of 3\n", attempt + 1);
        printf("Enter Username: ");
        if (fgets(username, sizeof(username), stdin) == NULL)
        {
            continue;
        }
        username[strcspn(username, "\n")] = '\0';

        printf("Enter Password: ");
        if (fgets(password, sizeof(password), stdin) == NULL)
        {
            continue;
        }
        password[strcspn(password, "\n")] = '\0';

        if (strcmp(username, correctUser) == 0 && strcmp(password, correctPass) == 0)
        {
            return 1;
        }
        else
        {
            printf("Invalid username or password! Try again.\n");
            attempt++;
        }
    }
    return 0;
}

void flushStdin(void)
{
    int c;
    while ((c = getchar()) != '\n');
}

void showMenu(void)
{
    int choice;

    while (1)
    {
        printf("\n===== Hostel Pass Monitoring System =====\n");
        printf("1. Add Pass Record\n");
        printf("2. View All Passes\n");
        printf("3. Search Pass by Student ID\n");
        printf("4. Delete a Record\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");
        if (scanf("%d", &choice) != 1)
        {
            printf("Invalid input. Please enter a number.\n");
            flushStdin();
            continue;
        }
        flushStdin();

        switch (choice)
        {
        case 1:
            addRecord();
            break;
        case 2:
            viewAllRecords();
            break;
        case 3:
            searchRecord();
            break;
        case 4:
            deleteRecord();
            break;
        case 5:
            printf("Thank you \n");
            return;
        default:
            printf("Invalid choice! Please try again.\n");
        }
    }
}

void addRecord(void)
{
    FILE *fp;
    struct PassRecord record;

    fp = fopen(FILENAME, "ab");
    if (fp == NULL)
    {
        printf("Error opening file");
        return;
    }

    printf("\nEnter Student ID: ");
    if (scanf("%d", &record.studentID) != 1)
    {
        printf("Invalid Student ID.\n");
        flushStdin();
        fclose(fp);
        return;
    }
    flushStdin();

    printf("Enter Name: ");
    if (fgets(record.name, sizeof(record.name), stdin) == NULL)
    {
        strcpy(record.name, "");
    }
    else
    {
        record.name[strcspn(record.name, "\n")] = '\0';
    }

    printf("Enter Pass Type (Day Pass / Leave Pass / Night Out): ");
    if (fgets(record.passType, sizeof(record.passType), stdin) == NULL)
    {
        strcpy(record.passType, "");
    }
    else
    {
        record.passType[strcspn(record.passType, "\n")] = '\0';
    }

    printf("Enter Date (DD/MM/YYYY): ");
    if (fgets(record.date, sizeof(record.date), stdin) == NULL)
    {
        strcpy(record.date, "");
    }
    else
    {
        record.date[strcspn(record.date, "\n")] = '\0';
    }

    printf("Enter Reason: ");
    if (fgets(record.reason, sizeof(record.reason), stdin) == NULL)
    {
        strcpy(record.reason, "");
    }
    else
    {
        record.reason[strcspn(record.reason, "\n")] = '\0';
    }

    if (fwrite(&record, sizeof(struct PassRecord), 1, fp) != 1)
    {
        printf("Error writing record");
    }
    else
    {
        printf("Record added successfully!\n");
    }

    fclose(fp);
}

void viewAllRecords(void)
{
    FILE *fp;
    struct PassRecord record;
    int count = 0;

    fp = fopen(FILENAME, "rb");
    if (fp == NULL)
    {
        printf("No records found yet!\n");
        return;
    }

    printf("\n----- All Pass Records -----\n");

    while (fread(&record, sizeof(struct PassRecord), 1, fp) == 1)
    {
        printf("\nStudent ID: %d\n", record.studentID);
        printf("Name: %s\n", record.name);
        printf("Pass Type: %s\n", record.passType);
        printf("Date: %s\n", record.date);
        printf("Reason: %s\n", record.reason);
        printf("-----------------------------\n");
        count++;
    }

    if (count == 0)
    {
        printf("No records to display!\n");
    }

    fclose(fp);
}

void searchRecord(void)
{
    FILE *fp;
    struct PassRecord record;
    int id, found = 0;

    fp = fopen(FILENAME, "rb");
    if (fp == NULL)
    {
        printf("No records found yet!\n");
        return;
    }

    printf("Enter Student ID to search: ");
    if (scanf("%d", &id) != 1)
    {
        printf("Invalid input.\n");
        flushStdin();
        fclose(fp);
        return;
    }
    flushStdin();

    while (fread(&record, sizeof(struct PassRecord), 1, fp) == 1)
    {
        if (record.studentID == id)
        {
            printf("\nRecord Found:\n");
            printf("Student ID: %d\n", record.studentID);
            printf("Name: %s\n", record.name);
            printf("Pass Type: %s\n", record.passType);
            printf("Date: %s\n", record.date);
            printf("Reason: %s\n", record.reason);
            found = 1;
            break;
        }
    }

    if (found == 0)
    {
        printf("No record found with Student ID %d\n", id);
    }
    fclose(fp);
}

void deleteRecord(void)
{
    FILE *fp, *temp;
    struct PassRecord record;
    int id, found = 0;
    const char tempName[] = "temp_pass_records.tmp";

    fp = fopen(FILENAME, "rb");
    if (fp == NULL)
    {
        printf("No records found yet!\n");
        return;
    }

    temp = fopen(tempName, "wb");
    if (temp == NULL)
    {
        printf("Error creating temporary file");
        fclose(fp);
        return;
    }

    printf("Enter Student ID to delete: ");
    if (scanf("%d", &id) != 1)
    {
        printf("Invalid input.\n");
        flushStdin();
        fclose(fp);
        fclose(temp);
        remove(tempName);
        return;
    }
    flushStdin();

    while (fread(&record, sizeof(struct PassRecord), 1, fp) == 1)
    {
        if (record.studentID == id)
        {
            found = 1;
            continue;
        }
        if (fwrite(&record, sizeof(struct PassRecord), 1, temp) != 1)
        {
            printf("Error writing to temporary file");
            fclose(fp);
            fclose(temp);
            remove(tempName);
            return;
        }
    }

    fclose(fp);
    fclose(temp);

    if (found)
    {
        if (remove(FILENAME) != 0)
        {
            printf("Error removing original file");
            return;
        }
        if (rename(tempName, FILENAME) != 0)
        {
            printf("Error renaming temporary file");
            return;
        }
        printf("Record deleted successfully!\n");
    }
    else
    {
        remove(tempName);
        printf("No record found with Student ID %d\n", id);
    }
}
