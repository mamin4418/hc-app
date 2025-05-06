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
-- Table structure for table `company_attribute`
--

DROP TABLE IF EXISTS `company_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_attribute` (
  `company_id` int NOT NULL,
  `attribute` varchar(16) NOT NULL,
  `name` varchar(45) NOT NULL,
  `address` varchar(45) NOT NULL,
  `city` varchar(45) DEFAULT NULL,
  `state` varchar(12) DEFAULT NULL,
  `zip` varchar(10) DEFAULT NULL,
  `email` varchar(96) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `routing` varchar(16) DEFAULT NULL,
  `account` varchar(20) DEFAULT NULL,
  `login` varchar(45) DEFAULT NULL,
  `other` varchar(45) DEFAULT NULL,
  `logo` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`company_id`,`attribute`,`name`,`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_attribute`
--

LOCK TABLES `company_attribute` WRITE;
/*!40000 ALTER TABLE `company_attribute` DISABLE KEYS */;
INSERT INTO `company_attribute` VALUES (1,'BANK','Members 1st FCU','15 North Lockwillow Avenue','Harrisbug','PA','17112','NossM@members1st.org','800-237-7288','231 382 241','7779647978',NULL,NULL,'members1st.png'),(1,'EPAY','Cash App','',NULL,NULL,NULL,'payments@himalayaproperties.org',NULL,NULL,NULL,'$HimalayaProperties',NULL,'cashapp.png'),(1,'EPAY','Venmo','',NULL,NULL,NULL,'payments@himalayaproperties.org',NULL,NULL,NULL,'@HimalayaProperties',NULL,'venmo.png'),(1,'EPAY','Zelle','',NULL,NULL,NULL,'payments@himalayaproperties.org','',NULL,NULL,'payments@himalayaproperties.org',NULL,'zelle.jpg'),(1,'SUPPORT','Heavy Lifting Property Mgmt','204 King Avenue','Harrisburg','PA','17109','support@himalayaproperties.org','646-780-5001',NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `company_attribute` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:23
