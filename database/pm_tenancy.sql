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
-- Table structure for table `tenancy`
--

DROP TABLE IF EXISTS `tenancy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenancy` (
  `tenancy_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `property_id` int NOT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `move_in` datetime DEFAULT CURRENT_TIMESTAMP,
  `move_out` datetime DEFAULT NULL,
  `family_members` int NOT NULL DEFAULT '1',
  `rent` double DEFAULT '0',
  `deposit` double DEFAULT '0',
  `deposit_a` double NOT NULL DEFAULT '0',
  `responsible` varchar(128) NOT NULL DEFAULT '0',
  `email` varchar(128) DEFAULT 'support@himalayaproperties.org',
  `phone` varchar(128) DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  `term` varchar(24) DEFAULT '1Y',
  `description` varchar(512) DEFAULT NULL,
  `updatedby` varchar(45) DEFAULT NULL,
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tenancy_id`),
  UNIQUE KEY `tenancy_id_UNIQUE` (`tenancy_id`),
  KEY `tn_idx2` (`tenant_id`,`property_id`,`start_date`) /*!80000 INVISIBLE */,
  KEY `tn_id3` (`property_id`,`tenant_id`,`start_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy`
--

LOCK TABLES `tenancy` WRITE;
/*!40000 ALTER TABLE `tenancy` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy` ENABLE KEYS */;
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
