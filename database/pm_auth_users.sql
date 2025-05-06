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
-- Table structure for table `auth_users`
--

DROP TABLE IF EXISTS `auth_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_users` (
  `user_id` bigint NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `last_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `address` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `address2` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `state` varchar(45) DEFAULT NULL,
  `zip` varchar(12) DEFAULT NULL,
  `email` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `login` varchar(24) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `password` varchar(24) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `phone` varchar(24) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `status` int NOT NULL DEFAULT '1',
  `avatar` varchar(45) DEFAULT 'assets/img/avatar_generic.png',
  `navigation` varchar(45) NOT NULL DEFAULT '/t',
  `id_value` int NOT NULL DEFAULT '0',
  `id_type` varchar(45) DEFAULT 'tenant_id',
  `createdby` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT 'HC',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `UK_ew1hvam8uwaknuaellwhqchhb` (`login`)
) ENGINE=InnoDB AUTO_INCREMENT=1098 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_users`
--

LOCK TABLES `auth_users` WRITE;
/*!40000 ALTER TABLE `auth_users` DISABLE KEYS */;
INSERT INTO `auth_users` VALUES (1,'Manoj','Amin','PO Box 396','','Princeton','NJ','08540','manoj@gmail.com','manoj.amin','a1b2c3d4e5f6','+1-347-401-0261',1,'assets/img/avatar.png','/admin',0,'tenant_id','PP','2020-03-16 20:21:35','PP','2021-08-18 20:50:43'),(2,'Trupti','Patel','PO Box 396',NULL,'Princeton','NJ','08540','ami@gmail.com','ami.amin','a1b2c3d4e5f6','+1-732-762-4899',1,'assets/img/anime6.png','/sm',0,'tenant_id','PP','2020-03-16 20:21:35','PP','2020-03-16 20:21:35'),(55,'Bedabati','Soni','','','','','','bedabati@himalayaproperties.org','bedabati','3acf8322b6b0','+91-97250-03022',1,'assets/img/avatar_generic.png','/sm',51,'vendor_id','PP','2020-10-22 20:46:43','HC','2022-11-10 16:41:35');
/*!40000 ALTER TABLE `auth_users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:22
