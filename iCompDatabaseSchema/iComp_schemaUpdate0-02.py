import sys

if sys.version_info[0] < 3:
    sys.stdout.write("\n\nRun with python3\n\n")
    sys.exit()
else:
    pass

##Creates .sql file to use to create iComp database
dbName      = input('Enter Database Name:  ')
useDB    = "use `" + dbName + "`;\n"

mainScript = """
ALTER TABLE `requestedChanges`
  ADD COLUMN `curFastLap` text  CHARACTER SET latin1 AFTER `week`,
  ADD COLUMN `newFastLap` text  CHARACTER SET latin1 AFTER `curFastLap`,
  ADD COLUMN `curQualPos` int(11) NOT NULL AFTER `newFastLap`,
  ADD COLUMN `newQualPos` int(11) NOT NULL AFTER `curQualPos`;

ALTER TABLE `scoring`
  ADD COLUMN `qualPosition` int(11) NOT NULL AFTER `fastLap`,
  ADD COLUMN `posGain` int(11) NOT NULL AFTER `qualPosition`;

ALTER TABLE `event`
  ADD COLUMN `enableHardChargerBonus` int(11) NOT NULL AFTER `winner`;

DROP TABLE IF EXISTS `iComp_schema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iComp_schema` (
  `version` text CHARACTER SET latin1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
LOCK TABLES `iComp_schema` WRITE;
/*!40000 ALTER TABLE `iComp_schema` DISABLE KEYS */;
INSERT INTO `iComp_schema` VALUES ('0.02');
/*!40000 ALTER TABLE `iComp_schema` ENABLE KEYS */;
UNLOCK TABLES;
"""


fh = open("./iComp_schemaUpdate0-02.sql",'w')
fh.write(useDB)
fh.write(mainScript)
fh.close()


sys.stdout.write('\n\nCreated script at ./iComp_schemaUpdate0-02.sql\n')
sys.stdout.write('Run this script on your mysql server to create database for iCompetition\n')
