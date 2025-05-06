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
-- Table structure for table `tenancy_applications`
--

DROP TABLE IF EXISTS `tenancy_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenancy_applications` (
  `tenancy_app_id` int NOT NULL AUTO_INCREMENT,
  `property_id` int DEFAULT NULL,
  `application` json NOT NULL,
  `status` varchar(16) NOT NULL DEFAULT 'NEW',
  `note` varchar(512) DEFAULT NULL,
  `updatedby` varchar(45) DEFAULT NULL,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `app_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `credit_score` double NOT NULL DEFAULT '0',
  `identification` varchar(45) NOT NULL DEFAULT '',
  `income_proof` varchar(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`tenancy_app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='New Tenant Applications';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_applications`
--

LOCK TABLES `tenancy_applications` WRITE;
/*!40000 ALTER TABLE `tenancy_applications` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_applications` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:26
