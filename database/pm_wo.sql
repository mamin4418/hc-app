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
-- Table structure for table `wo`
--

DROP TABLE IF EXISTS `wo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wo` (
  `wo_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `category_id` int NOT NULL DEFAULT '-1',
  `property_id` int NOT NULL,
  `priority` int NOT NULL DEFAULT '2',
  `title` varchar(128) NOT NULL,
  `description` varchar(512) DEFAULT NULL,
  `coordinator` int NOT NULL DEFAULT '0',
  `tags` varchar(128) DEFAULT NULL COMMENT 'Tags of the WO',
  `status` int NOT NULL DEFAULT '1',
  `reporting_method` int NOT NULL,
  `reportedby` varchar(64) NOT NULL,
  `entry` varchar(12) NOT NULL DEFAULT 'NO',
  `contact_name` varchar(45) NOT NULL,
  `contact_info` varchar(64) NOT NULL,
  `pet` varchar(12) DEFAULT 'NO',
  `availability` varchar(128) NOT NULL DEFAULT 'ALL DAY',
  `createdby` int NOT NULL DEFAULT '0',
  `tdate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `owner` varchar(64) NOT NULL DEFAULT 'NA',
  `updatedby` varchar(64) NOT NULL,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`wo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wo`
--

LOCK TABLES `wo` WRITE;
/*!40000 ALTER TABLE `wo` DISABLE KEYS */;
/*!40000 ALTER TABLE `wo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:29
