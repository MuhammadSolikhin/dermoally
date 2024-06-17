-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 14, 2024 at 03:50 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_dermoally`
--

-- --------------------------------------------------------

--
-- Table structure for table `disease`
--

CREATE TABLE `disease` (
  `id_disease` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `overview` text DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `disease`
--

INSERT INTO `disease` (`id_disease`, `name`, `overview`, `image_url`) VALUES
(1, 'Acne', 'Acne is a common skin condition characterized by the formation of comedones (blackheads and whiteheads), papules, pustules, nodules, and cysts. It is caused by the blockage of pores with dead skin cells, oil, and bacteria. Acne can occur on various parts of the body, but it is most common on the face, particularly on the forehead, nose, and chin. Symptoms include redness, inflammation, and scarring.', NULL),
(2, 'Actinic Keratosis', 'Actinic keratosis (AK) is a precancerous skin condition caused by prolonged exposure to ultraviolet (UV) radiation. It appears as rough, scaly patches or bumps on sun-damaged skin, often on the face, ears, neck, and hands. AK can progress to squamous cell carcinoma if left untreated. Symptoms include itching, tenderness, or stinging, and the condition is more common in older individuals with lighter skin types.', NULL),
(3, 'Blackheads', 'Blackheads are a type of comedone that occurs when pores on the skin become clogged with dead skin cells, oil, and bacteria. They appear as small, dark spots on the skin, often on the nose, forehead, and chin. Blackheads are more common in people with oily skin.', NULL),
(4, 'Contagios Molluscum', 'Molluscum contagiosum is a viral infection that causes small, painless bumps on the skin. It is highly contagious and can spread through skin-to-skin contact. Symptoms include small, round, pink or white bumps that can appear anywhere on the body.', NULL),
(5, 'Herpes', 'Herpes is a viral infection that causes cold sores or fever blisters on the skin. It is highly contagious and can spread through skin-to-skin contact. Symptoms include small, painful blisters that can appear on the lips, face, or other parts of the body.', NULL),
(6, 'Keloid', 'Keloids are raised, thick scars that can form after skin injuries, such as cuts, burns, or surgical incisions. They are caused by an overactive response to injury, leading to excessive collagen production. Symptoms include raised, red, and itchy scars that can be painful.', NULL),
(7, 'Keratosis Seborrheic', 'Keratosis seborrheic is a benign skin condition characterized by the formation of small, rough, and scaly patches on the skin. It is caused by the accumulation of keratin, a protein found in skin cells. Symptoms include small, rough patches on the face, chest, and back.', NULL),
(8, 'Milia', 'Milia are small, white bumps that form on the skin, often on the face, nose, and cheeks. They are caused by the blockage of pores with keratin and oil. Symptoms include small, white bumps that can appear anywhere on the body.', NULL),
(9, 'Pityriasis Versicolor', 'Pityriasis versicolor, also known as tinea versicolor, is a common, non-contagious fungal infection of the skin that causes discolored patches to appear. The patches can be flat and round, scaly, and sometimes itchy. They can appear on the chest, upper back, upper arms, neck, or tummy.', NULL),
(10, 'Ringworm', 'Ringworm, also known as tinea corporis, is a contagious fungal infection of the skin that causes an itchy, circular rash. It usually starts as small red pimples that spread to form a ring with clearer skin in the middle. The rash can also be scaly and may cause hair loss in the affected area. Symptoms usually appear 4–14 days after exposure.', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `images`
--

CREATE TABLE `images` (
  `id_image` int(11) NOT NULL,
  `id_userimage` int(11) DEFAULT NULL,
  `image_url` varchar(255) NOT NULL,
  `date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `images`
--

INSERT INTO `images` (`id_image`, `id_userimage`, `image_url`, `date`) VALUES
(6, 1, 'http://localhost:9000/static/image_2024-06-14_184041_1.jpg', '2024-06-14 18:40:41'),
(7, 1, 'http://localhost:9000/static/image_2024-06-14_184631_1.jpg', '2024-06-14 18:46:31'),
(8, 1, 'http://localhost:9000/static/image_2024-06-14_184649_1.jpg', '2024-06-14 18:46:49'),
(9, 1, 'http://localhost:9000/static/image_2024-06-14_194224_1.jpg', '2024-06-14 19:42:24'),
(10, 3, 'http://localhost:9000/static/image_2024-06-14_201209_3.jpg', '2024-06-14 20:12:09'),
(11, 3, 'http://localhost:9000/static/image_2024-06-14_201358_3.jpg', '2024-06-14 20:13:58'),
(12, 3, 'http://localhost:9000/static/image_2024-06-14_204644_3.jpg', '2024-06-14 20:46:44');

-- --------------------------------------------------------

--
-- Table structure for table `medication_ingredients`
--

CREATE TABLE `medication_ingredients` (
  `id_medication` int(11) NOT NULL,
  `id_disease_medication` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `link_tokopedia` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `medication_ingredients`
--

INSERT INTO `medication_ingredients` (`id_medication`, `id_disease_medication`, `name`, `image_url`, `link_tokopedia`) VALUES
(1, 1, 'Niacinamide', NULL, NULL),
(2, 1, 'Benzoyl Peroxide', NULL, NULL),
(3, 1, 'Retinoids (e.g. Tretinoin, Adapalene)', NULL, NULL),
(4, 1, 'Salicylic Acid', NULL, NULL),
(5, 1, 'Antibiotics (e.g. Clindamycin)', NULL, NULL),
(6, 2, '5-fluorouracil (5-FU)', NULL, NULL),
(7, 2, 'Imiquimod', NULL, NULL),
(8, 2, 'Diclofenac', NULL, NULL),
(9, 3, 'Salicylic Acid', NULL, NULL),
(10, 3, 'Benzoyl Peroxide', NULL, NULL),
(11, 3, 'Retinoids (e.g. Adapalene)', NULL, NULL),
(12, 4, 'Cantharidin', NULL, NULL),
(13, 4, 'Imiquimod', NULL, NULL),
(14, 4, 'Potassium Hydroxide (KOH)', NULL, NULL),
(15, 4, 'Benzoyl Peroxide', NULL, NULL),
(16, 5, 'Acyclovir', NULL, NULL),
(17, 5, 'Valacyclovir', NULL, NULL),
(18, 5, 'Famciclovir', NULL, NULL),
(19, 6, 'Silicone Gel Sheets', NULL, NULL),
(20, 6, 'Corticosteroids (e.g. Triamcinolone)', NULL, NULL),
(21, 6, 'Imiquimod', NULL, NULL),
(22, 7, 'Hydrogen Peroxide', NULL, NULL),
(23, 7, 'Alpha-hydroxy Acids (AHAs)', NULL, NULL),
(24, 7, 'Beta-hydroxy Acids (BHAs)', NULL, NULL),
(25, 8, 'Retinoids (e.g. Tretinoin)', NULL, NULL),
(26, 8, 'AHAs and BHAs', NULL, NULL),
(27, 8, 'Salicylic Acid', NULL, NULL),
(28, 8, 'Glycolic Acid', NULL, NULL),
(29, 9, 'Selenium Sulfide', NULL, NULL),
(30, 9, 'Terbinafine', NULL, NULL),
(31, 9, 'Ketoconazole', NULL, NULL),
(32, 9, 'Zinc Pyrithione', NULL, NULL),
(33, 10, 'Clotrimazole', NULL, NULL),
(34, 10, 'Terbinafine', NULL, NULL),
(35, 10, 'Miconazole', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `skin_analyze`
--

CREATE TABLE `skin_analyze` (
  `id_analyze` int(11) NOT NULL,
  `id_useranalyze` int(11) DEFAULT NULL,
  `id_imageanalyze` int(11) DEFAULT NULL,
  `acne` float DEFAULT NULL,
  `actinickeratosis` float DEFAULT NULL,
  `blackheads` float DEFAULT NULL,
  `herpes` float DEFAULT NULL,
  `keloid` float DEFAULT NULL,
  `keratosisseborrheic` float DEFAULT NULL,
  `milia` float DEFAULT NULL,
  `pityriasis_versicolor` float DEFAULT NULL,
  `ringworm` float DEFAULT NULL,
  `date_analyze` datetime NOT NULL,
  `skin_health` int(11) DEFAULT NULL,
  `favorite` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `skin_analyze`
--

INSERT INTO `skin_analyze` (`id_analyze`, `id_useranalyze`, `id_imageanalyze`, `acne`, `actinickeratosis`, `blackheads`, `herpes`, `keloid`, `keratosisseborrheic`, `milia`, `pityriasis_versicolor`, `ringworm`, `date_analyze`, `skin_health`, `favorite`) VALUES
(1, 1, 6, 0.0220518, 0.00030663, 0.00849455, 0.000306528, 0.02552, 0.0000836125, 0.0831741, 0.859497, 0.000566183, '2024-06-14 18:40:41', 90, 0),
(2, 1, 7, 0.356205, 0.021429, 0.196706, 0.036427, 0.24718, 0.00805616, 0.122631, 0.00454311, 0.00682294, '2024-06-14 18:46:31', 100, 0),
(3, 1, 8, 0.0692011, 0.0000411232, 0.852709, 0.0000533615, 0.00737669, 0.000211279, 0.0701262, 0.000236172, 0.000045601, '2024-06-14 18:46:49', 90, 0),
(4, 1, 9, 0.00320545, 0.00260351, 0.00168075, 0.00359969, 0.058784, 0.000283138, 0.00628049, 0.922059, 0.00150417, '2024-06-14 19:42:24', 91, 0),
(5, 3, 10, 0.324569, 0.0197854, 0.0117331, 0.0221425, 0.207263, 0.000790236, 0.00431579, 0.40781, 0.00159063, '2024-06-14 20:12:09', 100, 0),
(6, 3, 11, 0.962161, 0.0071801, 0.00759283, 0.000118925, 0.0224209, 0.0000272556, 0.000273514, 0.000153568, 0.0000717966, '2024-06-14 20:13:58', 93, 0),
(7, 3, 12, 0.000460527, 0.0000173659, 0.00000291229, 0.00000747743, 0.998707, 0.000000630692, 0.00000184557, 0.000800648, 0.00000153317, '2024-06-14 20:46:44', 93, 0);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `profile_image_url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id_user`, `username`, `password`, `email`, `name`, `profile_image_url`) VALUES
(1, 'azzandr', 'scrypt:32768:8:1$r3sQdTyg3UwmRDFP$143d8ca42031d7377f7cb31a38317ce145e8d2cbb9fa3ee9b4b916b9d5a766ab1a28a78e0236aed445240ffd9a1881c64e862b88fcddc3714697806357d12656', 'azzan@example.com', 'Azzan Dwi Riski', NULL),
(2, 'thoriq', 'scrypt:32768:8:1$AtbBSW4KWSpbrx3H$d076b8659af2e0f51ce510b4ce4cd80a83d20348f9c708aefd8a1430f403e40b7b0f15e3baacc096dac341fc8ea02c32a5c193ac058d3bfb18f1830390b15195', 'thoriq@example.com', 'Thoriq Maulidka', NULL),
(3, 'sofia', 'scrypt:32768:8:1$KIbpu78rOLHZimPo$deb8325ef77710cc1a8941ca537167b6801a2b1fb24055d890ba4442698997e62bd02c38044e1a06963eb3fc024687bce8b6142ce4bdb31f01cd54fca8aadb43', 'sofia@example.com', 'Sofia Fei', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `disease`
--
ALTER TABLE `disease`
  ADD PRIMARY KEY (`id_disease`);

--
-- Indexes for table `images`
--
ALTER TABLE `images`
  ADD PRIMARY KEY (`id_image`),
  ADD KEY `id_userimage` (`id_userimage`);

--
-- Indexes for table `medication_ingredients`
--
ALTER TABLE `medication_ingredients`
  ADD PRIMARY KEY (`id_medication`),
  ADD KEY `id_disease_medication` (`id_disease_medication`);

--
-- Indexes for table `skin_analyze`
--
ALTER TABLE `skin_analyze`
  ADD PRIMARY KEY (`id_analyze`),
  ADD KEY `id_useranalyze` (`id_useranalyze`),
  ADD KEY `id_imageanalyze` (`id_imageanalyze`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `disease`
--
ALTER TABLE `disease`
  MODIFY `id_disease` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `images`
--
ALTER TABLE `images`
  MODIFY `id_image` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `medication_ingredients`
--
ALTER TABLE `medication_ingredients`
  MODIFY `id_medication` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `skin_analyze`
--
ALTER TABLE `skin_analyze`
  MODIFY `id_analyze` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `images`
--
ALTER TABLE `images`
  ADD CONSTRAINT `images_ibfk_1` FOREIGN KEY (`id_userimage`) REFERENCES `users` (`id_user`);

--
-- Constraints for table `medication_ingredients`
--
ALTER TABLE `medication_ingredients`
  ADD CONSTRAINT `medication_ingredients_ibfk_1` FOREIGN KEY (`id_disease_medication`) REFERENCES `disease` (`id_disease`);

--
-- Constraints for table `skin_analyze`
--
ALTER TABLE `skin_analyze`
  ADD CONSTRAINT `skin_analyze_ibfk_1` FOREIGN KEY (`id_useranalyze`) REFERENCES `users` (`id_user`),
  ADD CONSTRAINT `skin_analyze_ibfk_2` FOREIGN KEY (`id_imageanalyze`) REFERENCES `images` (`id_image`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
