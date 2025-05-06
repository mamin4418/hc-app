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
-- Table structure for table `auth_authority`
--

DROP TABLE IF EXISTS `auth_authority`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_authority` (
  `authority_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(128) DEFAULT NULL,
  `component` varchar(64) NOT NULL,
  `icon` varchar(45) DEFAULT NULL,
  `class` varchar(45) DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  `updatedby` varchar(64) DEFAULT NULL,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`authority_id`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_authority`
--

LOCK TABLES `auth_authority` WRITE;
/*!40000 ALTER TABLE `auth_authority` DISABLE KEYS */;
INSERT INTO `auth_authority` VALUES (1,'Home','Main Landing Page','dashboard','fab fa-centercode',NULL,1,'INIT','2020-03-28 11:27:46'),(2,'Company',NULL,'company','fas fa-building',NULL,1,'INIT','2020-03-28 11:27:46'),(3,'Cashflow',NULL,'cashflow','fab fa-monero',NULL,1,'INIT','2020-03-28 11:27:46'),(4,'Property Details',NULL,'property','fas fa-home',NULL,1,'INIT','2020-03-28 11:27:46'),(5,'Property Edit',NULL,'propertye','fas fa-edit',NULL,1,'INIT','2020-03-28 11:27:46'),(6,'Tenant Details',NULL,'tenant','fas fa-user',NULL,1,'INIT','2020-03-28 11:27:46'),(7,'Tenant Edit',NULL,'tenante','fas fa-edit',NULL,1,'INIT','2020-03-28 11:27:46'),(8,'Workorder',NULL,'wo','fas fa-edit',NULL,1,'INIT','2020-03-28 11:27:46'),(9,'Workorder Creation',NULL,'wo','fas fa-edit',NULL,1,'INIT','2020-03-28 11:27:46'),(10,'Tenancy Edit',NULL,'tenancye','fas fa-edit',NULL,1,'INIT','2020-03-29 00:09:57'),(11,'User',NULL,'user','fas fa-user-cog',NULL,1,'INIT','2020-03-29 00:09:57'),(12,'Reports',NULL,'report','fas fa-th-list',NULL,1,'INIT','2020-03-29 00:09:57'),(13,'DM',NULL,'dm','fas fa-table',NULL,1,'INIT','2020-03-29 00:09:57'),(14,'Workorder',NULL,'wo','fas fa-toolbox',NULL,1,'INIT','2020-03-29 00:09:57'),(15,'WO Management',NULL,'wom','fas fa-tasks',NULL,1,'INIT','2020-03-29 00:09:57'),(16,'Transactions',NULL,'tx','fas fa-list',NULL,1,'INIT','2020-03-29 00:09:57'),(17,'Documents','List of documents','documents','fas fa-folder-open',NULL,1,'INIT','2020-04-05 16:08:38'),(18,'Tenancy','Tenancy View','tenancy','fas fa-user-circle',NULL,1,'INIT','2020-04-06 02:04:58'),(19,'Payment','Payment information','payment','fas fa-money-bill-alt',NULL,1,'INIT','2020-04-27 10:37:02'),(20,'Investor','Investor Page','investor','fas fa-user-tie',NULL,1,'INIT','2020-09-27 18:22:36'),(21,'Vendor','Vendor','vendor','fas fa-toolbox',NULL,1,'INIT','2020-10-24 02:27:26'),(22,'Admins','Admin Tools','admins','fas fa-users-cog',NULL,1,'INIT','2021-02-13 20:26:52'),(23,'Applications','Application Management','applications','fab fa-wpforms',NULL,1,'INIT','2021-02-13 20:26:52'),(24,'Tranche',NULL,'tranche','fab fa-wpforms',NULL,1,'INIT','2021-05-22 23:37:35'),(25,'Tranche Edit',NULL,'tranchee','fab fa-wpforms',NULL,1,'INI','2021-05-22 23:37:35'),(26,'Analysis','Analysis Page','analysis','fab fa-wpformd',NULL,1,'INIT','2023-05-05 02:43:27');
/*!40000 ALTER TABLE `auth_authority` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:20
