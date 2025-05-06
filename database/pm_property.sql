-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: pm
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `property`
--

DROP TABLE IF EXISTS `property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `property` (
  `property_id` int NOT NULL,
  `llc` varchar(64) NOT NULL,
  `tranche_id` int NOT NULL DEFAULT '0',
  `group` varchar(64) DEFAULT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime DEFAULT NULL,
  `label` varchar(64) NOT NULL,
  `label2` varchar(128) DEFAULT NULL,
  `street` varchar(96) DEFAULT NULL,
  `unit` varchar(12) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `state` varchar(2) DEFAULT NULL,
  `zip` varchar(6) DEFAULT NULL,
  `parent` int DEFAULT NULL,
  `tax_id` varchar(45) DEFAULT NULL,
  `p_type` varchar(45) DEFAULT NULL,
  `built` int DEFAULT NULL,
  `size` varchar(45) DEFAULT NULL,
  `bed` double DEFAULT NULL,
  `bath` double DEFAULT NULL,
  `total_rooms` double DEFAULT '2',
  `p_status` varchar(45) DEFAULT NULL,
  `market_rent` double DEFAULT '0',
  `sub_units` int NOT NULL DEFAULT '1',
  `location` varchar(45) DEFAULT NULL,
  `description` varchar(1048) DEFAULT NULL,
  `updatedby` varchar(45) NOT NULL DEFAULT 'INIT',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`property_id`),
  KEY `p_label` (`label`,`city`,`state`),
  KEY `company` (`llc`,`group`,`label`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property`
--

LOCK TABLES `property` WRITE;
/*!40000 ALTER TABLE `property` DISABLE KEYS */;
INSERT INTO `property` VALUES (0,'MASTER',0,'MASTER','2001-01-01 00:00:00',NULL,'UNKNOWN','UNKNOWN','UNKNOWN','','NA','NA','00000',0,'','NA',0,'0',0,0,0,'RENT READY',0,1,NULL,NULL,'INIT','2020-02-08 16:59:33'),(1,'HC',1,'MOR','0000-00-00 00:00:00','2024-07-01 00:00:00','28 Harrison St','28H-M','28 Harrison Street','','Morristown','NJ','7960',1,'09-067-010-000-0000','MFR - 3 Story',1950,'2000',4,2,10,'MASTER',4000,2,'Floor: 1, Side: R, Door: 1','','HP','2024-10-03 13:08:50'),(2,'HC',1,'MOR','2009-09-11 00:00:00',NULL,'28 Harrison St','28H','28 Harrison Street','','Morristown','NJ','7960',155,'09-067-010-000-0000','MFR - 3 Story',0,'0',2,1,5,'RENT READY',2000,1,NULL,NULL,'INIT','2020-02-08 16:59:33'),(3,'HC',1,'MOR','2009-09-12 00:00:00',NULL,'28 1/2 Harrison St','285H','28 1/2 Harrison Street','','Morristown','NJ','7960',155,'09-067-010-000-0000','MFR - 3 Story',0,'0',2,1,5,'RENT READY',1735,1,NULL,NULL,'INIT','2020-02-08 16:59:33');
/*!40000 ALTER TABLE `property` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:28
