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
DROP TABLE IF EXISTS `topLap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `topLap` (
  `eventNum` int(11) NOT NULL,
  `weekNum` int(11) NOT NULL,
  `userNum` int(11) NOT NULL,
  `laptime` text CHARACTER SET latin1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `iComp_schema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iComp_schema` (
  `version` text CHARACTER SET latin1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
LOCK TABLES `iComp_schema` WRITE;
/*!40000 ALTER TABLE `iComp_schema` DISABLE KEYS */;
INSERT INTO `iComp_schema` VALUES ('0.01');
/*!40000 ALTER TABLE `iComp_schema` ENABLE KEYS */;
UNLOCK TABLES;

ALTER TABLE `event`
  ADD COLUMN `enableFastLapBonus` int(11) NOT NULL AFTER `live`,
  ADD COLUMN `finished` int(11) NOT NULL DEFAULT 0 AFTER `enableFastLapBonus`,
  ADD COLUMN `winner` text CHARACTER SET latin1 DEFAULT NULL AFTER `finished`;

ALTER TABLE `scoring`
  ADD COLUMN `fastLap` text CHARACTER SET latin1 DEFAULT NULL AFTER `changeRequested`;

ALTER TABLE `users`
  ADD COLUMN `wins` int(11) NOT NULL DEFAULT 0 AFTER `email`;
"""

fh = open("./iComp_schemaUpdate0-01.sql",'w')
fh.write(useDB)
fh.write(mainScript)
fh.close()


sys.stdout.write('\n\nCreated script at ./iComp_schemaUpdate0-01.sql\n')
sys.stdout.write('Run this script on your mysql server to create database for iCompetition\n')
