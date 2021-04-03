Availble Scripts - 
 - iComp_genNewDbCreateScript.py:
   - Creates the mysql script needed to create fresh install of base iCompetition database.
   - run script to generate .sql file.  
   - on database server, run mysql < path/to/generated/file
 - iComp_updateFrom1-00To1-01.py
   - Creates the mysql script needed to upgrade the database schema from version 1.00 to version 1.01.
     - This is required to run when updating to iCompeition version 1.01.xx from a lower version.
   - on database server, run mysql < path/to/generated/file