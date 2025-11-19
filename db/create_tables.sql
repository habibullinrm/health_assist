-- Таблица ролей пользователей
CREATE TABLE roles
(
  id SERIAL PRIMARY KEY,
  type VARCHAR(32) NOT NULL UNIQUE
);

-- Уведомления для пользователей
CREATE TABLE notifications
(
  id SERIAL PRIMARY KEY,
  type VARCHAR(50) NOT NULL CHECK (type IN ('appointment', 'prescription', 'test', 'reminder', 'alert')),
  time TIMESTAMP WITH TIME ZONE NOT NULL,
  title VARCHAR(128) NOT NULL,
  message TEXT,
  is_read BOOLEAN NOT NULL DEFAULT false,
  user_id INT NOT NULL,
  medical_entity_id INT, -- ID связанной сущности (appointment/prescription/test)
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);

-- Справочник лекарственных препаратов
CREATE TABLE medicins
(
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  international_name VARCHAR(255) NOT NULL,
  form VARCHAR(100) NOT NULL,
  atc_code VARCHAR(20) NOT NULL,
  instruction TEXT NOT NULL
);

CREATE INDEX idx_medicins_atc_code ON medicins(atc_code);

-- Справочник врачей
CREATE TABLE doctors
(
  id SERIAL PRIMARY KEY,
  external_id VARCHAR(100) NOT NULL UNIQUE,
  full_name VARCHAR(255) NOT NULL,
  specialization VARCHAR(100) NOT NULL
);

-- Пользователи системы
CREATE TABLE users
(
  id SERIAL PRIMARY KEY,
  external_id VARCHAR(100) NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sex VARCHAR(10) NOT NULL CHECK (sex IN ('male', 'female', 'other')),
  age INT NOT NULL CHECK (age >= 0 AND age <= 150),
  full_name VARCHAR(255) NOT NULL,
  phone VARCHAR(20) NOT NULL UNIQUE,
  role_id INT NOT NULL,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

CREATE INDEX idx_users_role_id ON users(role_id);

-- Планы лечения пациентов
CREATE TABLE plans
(
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'completed', 'cancelled', 'pending')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  share_with_doctor BOOLEAN NOT NULL DEFAULT false,
  doctor_id INT NOT NULL,
  user_id INT NOT NULL,
  FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_plans_user_id ON plans(user_id);
CREATE INDEX idx_plans_doctor_id ON plans(doctor_id);

-- Записи на приём к врачу
CREATE TABLE appointments
(
  id SERIAL PRIMARY KEY,
  doctor_specialization VARCHAR(100) NOT NULL,
  date TIMESTAMP WITH TIME ZONE NOT NULL,
  status VARCHAR(50) NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled', 'missed')),
  plan_id INT NOT NULL,
  FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
);

CREATE INDEX idx_appointments_plan_id ON appointments(plan_id);

-- Медицинские назначения (рецепты)
CREATE TABLE medical_prescriptions
(
  id SERIAL PRIMARY KEY,
  dosage NUMERIC(10, 2) NOT NULL CHECK (dosage > 0),
  quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0),
  duration_days INT NOT NULL CHECK (duration_days > 0),
  start_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  description TEXT,
  status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'completed', 'cancelled', 'expired')),
  repeat VARCHAR(100) NOT NULL,
  medicin_id INT NOT NULL,
  plan_id INT NOT NULL,
  FOREIGN KEY (medicin_id) REFERENCES medicins(id) ON DELETE RESTRICT,
  FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
);

CREATE INDEX idx_medical_prescriptions_plan_id ON medical_prescriptions(plan_id);
CREATE INDEX idx_medical_prescriptions_medicin_id ON medical_prescriptions(medicin_id);

-- Медицинские анализы и обследования
CREATE TABLE medical_tests
(
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  date TIMESTAMP WITH TIME ZONE NOT NULL,
  status VARCHAR(50) NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled', 'pending_results')),
  plan_id INT NOT NULL,
  FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
);

CREATE INDEX idx_medical_tests_plan_id ON medical_tests(plan_id);

-- Симптомы пациентов
CREATE TABLE symptoms
(
  id SERIAL PRIMARY KEY,
  description TEXT NOT NULL,
  plan_id INT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
);

CREATE INDEX idx_symptoms_plan_id ON symptoms(plan_id);

-- Опросы пациентов по симптомам
CREATE TABLE surveys
(
  id SERIAL PRIMARY KEY,
  date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  value INT NOT NULL CHECK (value >= 0 AND value <= 10),
  user_answer TEXT,
  symptom_id INT NOT NULL,
  FOREIGN KEY (symptom_id) REFERENCES symptoms(id) ON DELETE CASCADE
);

CREATE INDEX idx_surveys_symptom_id ON surveys(symptom_id);