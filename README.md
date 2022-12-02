# perqara-data
Contains all ETL and schedules for all data in Perqara

## What does it contains?
There are 3 folders:
- `dags`
> You can find schedule file for each period which might be run e.g. daily, weekly and etc.
- `data`
> It can be used to store data which will be used for our ETLs. This is only **temporary** storage. Do not store any file which has big file size since the VM storage is limited
- `plugins`
> It contains multiple plugin or generic function that can be used in the ETL process. Any process should be created with DRY (Don't Repeat Yourself) principal in mind.

## Troubleshooting and Question
Please contact `data@perqara.com` if you have any question on this repository