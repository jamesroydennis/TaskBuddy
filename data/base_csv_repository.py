# taskbuddy_project/data/base_csv_repository.py

import csv
import uuid
import os
from abc import abstractmethod
from typing import List, Optional, TypeVar, Generic, Dict, Any

from business.interfaces.ICrudRepository import ICrudRepository
from loguru import logger

# Define a TypeVar for the entity type
T = TypeVar('T')

class BaseCsvRepository(ICrudRepository[T]):
    """
    Abstract base class for CSV repositories, implementing generic CRUD operations.
    It uses the globally configured Loguru logger directly.
    Concrete subclasses must implement _to_dict and _from_dict for entity serialization.
    """
    def __init__(self, file_path: str, entity_name: str = "entity"):
        self.file_path = file_path
        self.entity_name = entity_name
        # Removed manual "DEBUG - " from message
        logger.debug(f"BaseCsvRepository initialized for {entity_name}s. File: {file_path}")
        self._expected_headers = ['id']


    @abstractmethod
    def _to_dict(self, entity: T) -> Dict[str, Any]:
        """
        Converts an entity object into a dictionary suitable for writing to a CSV row.
        Must be implemented by concrete subclasses.
        """
        pass

    @abstractmethod
    def _from_dict(self, row: Dict[str, str]) -> T:
        """
        Converts a dictionary (CSV row) into an entity object.
        Must be implemented by concrete subclasses.
        """
        pass

    def _write_all(self, entities: List[T]):
        """
        Internal helper method to write a list of entity objects back to the CSV file.
        This rewrites the entire file.
        """
        if not entities:
            mode = 'w'
            header_row = list(self._expected_headers)
            if header_row:
                try:
                    with open(self.file_path, mode=mode, newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=header_row)
                        writer.writeheader()
                    # Removed manual "DEBUG - " from message
                    logger.debug(f"Emptied CSV file '{self.file_path}' with header.")
                except Exception as e:
                    # Removed manual "ERROR - " from message
                    logger.error(f"Failed to empty CSV file '{self.file_path}' or write header: {e}", exc_info=True)
                    raise
            return

        sample_dict = self._to_dict(entities[0])
        fieldnames = list(sample_dict.keys())

        try:
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entity in entities:
                    writer.writerow(self._to_dict(entity))
            # Removed manual "DEBUG - " from message
            logger.debug(f"Successfully wrote {len(entities)} {self.entity_name}s to {self.file_path}.")
        except Exception as e:
            # Removed manual "ERROR - " from message
            logger.error(f"Failed to write {self.entity_name}s to CSV file '{self.file_path}': {e}", exc_info=True)
            raise


    def add(self, entity: T):
        """Adds a new entity."""
        # Removed manual "INFO - " from message
        logger.info(f"Attempting to add new {self.entity_name}: '{getattr(entity, 'title', entity.id)}' to {self.file_path}")
        
        existing_entities = []
        try:
            existing_entities = self.get_all()
        except FileNotFoundError:
            # Removed manual "DEBUG - " from message
            logger.debug(f"No existing CSV file found at {self.file_path}, creating new for add operation.")
            pass

        if any(getattr(e, 'id', None) == getattr(entity, 'id', None) for e in existing_entities):
            # Removed manual "WARNING - " from message
            logger.warning(f"{self.entity_name} with ID '{getattr(entity, 'id', 'N/A')}' already exists. Skipping add operation.")
            return

        existing_entities.append(entity)
        self._write_all(existing_entities)
        # Removed manual "INFO - " from message
        logger.info(f"Successfully added {self.entity_name} '{getattr(entity, 'title', entity.id)}' and wrote to {self.file_path}.")


    def get_by_id(self, entity_id: uuid.UUID) -> T:
        """Retrieves a single entity by ID."""
        # Removed manual "DEBUG - " from message
        logger.debug(f"Attempting to retrieve {self.entity_name} with ID: {entity_id}")
        all_entities = self.get_all()
        for entity in all_entities:
            if getattr(entity, 'id', None) == entity_id:
                # Removed manual "INFO - " from message
                logger.info(f"Found {self.entity_name} with ID {entity_id}")
                return entity
        # Removed manual "WARNING - " from message
        logger.warning(f"{self.entity_name} with ID '{entity_id}' not found in {self.file_path}.")
        raise ValueError(f"{self.entity_name} with ID '{entity_id}' not found.")


    def get_all(self) -> List[T]:
        """Retrieves all entities."""
        entities: List[T] = []
        try:
            if not os.path.exists(self.file_path):
                # Removed manual "WARNING - " from message
                logger.warning(f"CSV file not found at: {self.file_path}")
                raise FileNotFoundError(f"CSV file not found at: {self.file_path}")

            with open(self.file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                # Removed manual "DEBUG - " from message
                logger.debug(f"Successfully opened CSV file: {self.file_path}")

                first_line_content = csvfile.readline().strip()
                if not first_line_content:
                    # Removed manual "WARNING - " from message
                    logger.warning(f"CSV file '{self.file_path}' is empty or contains only whitespace.")
                    return []

                csvfile.seek(0)
                reader = csv.DictReader(csvfile)

                actual_fieldnames = reader.fieldnames
                if not actual_fieldnames:
                    # Removed manual "ERROR - " from message
                    logger.error(f"CSV file '{self.file_path}' has no header row or is malformed. Content: '{first_line_content}'")
                    return []

                missing_core_headers = [h for h in self._expected_headers if h not in actual_fieldnames]
                if missing_core_headers:
                    # Removed manual "ERROR - " from message
                    logger.error(f"Missing core headers in CSV: {missing_core_headers}. Found: {actual_fieldnames}")
                    return []

                # Removed manual "DEBUG - " from message
                logger.debug(f"CSV headers found: {actual_fieldnames}")

                for row_num, row in enumerate(reader):
                    try:
                        entity = self._from_dict(row)
                        entities.append(entity)
                    except (ValueError, KeyError, TypeError) as e:
                        # Removed manual "ERROR - " from message
                        logger.error(f"Data conversion/missing field error in row {row_num + 2}: {e}. Row: {row}", exc_info=False)
                    except Exception as e:
                        # Removed manual "ERROR - " from message
                        logger.error(f"Unexpected error processing row {row_num + 2}: {e}. Row: {row}", exc_info=False)

        except FileNotFoundError:
            # Removed manual "WARNING - " from message
            logger.warning(f"CSV file not found when attempting to read: {self.file_path}")
            raise
        except Exception as e:
            # Removed manual "CRITICAL - " from message
            logger.critical(f"An unhandled error occurred while processing CSV file '{self.file_path}': {e}", exc_info=True)
            raise

        # Removed manual "INFO - " from message
        logger.info(f"Successfully loaded {len(entities)} {self.entity_name}s from {self.file_path}")
        return entities


    def update(self, entity: T):
        """Updates an existing entity."""
        # Removed manual "INFO - " from message
        logger.info(f"Attempting to update {self.entity_name} with ID: '{getattr(entity, 'id', 'N/A')}' in {self.file_path}")
        
        existing_entities = self.get_all()
        
        found = False
        for i, existing_entity in enumerate(existing_entities):
            if getattr(existing_entity, 'id', None) == getattr(entity, 'id', None):
                existing_entities[i] = entity
                found = True
                break
        
        if not found:
            # Removed manual "WARNING - " from message
            logger.warning(f"{self.entity_name} with ID '{getattr(entity, 'id', 'N/A')}' not found for update in {self.file_path}.")
            raise ValueError(f"{self.entity_name} with ID '{getattr(entity, 'id', 'N/A')}' not found for update.")
        
        self._write_all(existing_entities)
        # Removed manual "INFO - " from message
        logger.info(f"Successfully updated {self.entity_name} with ID '{getattr(entity, 'id', 'N/A')}' and wrote to {self.file_path}.")

    def delete(self, entity_id: uuid.UUID):
        """Deletes an entity by its ID."""
        # Removed manual "INFO - " from message
        logger.info(f"Attempting to delete {self.entity_name} with ID: '{entity_id}' from {self.file_path}")
        
        existing_entities = self.get_all()
        
        initial_count = len(existing_entities)
        entities_after_deletion = [entity for entity in existing_entities if getattr(entity, 'id', None) != entity_id]
        
        if len(entities_after_deletion) == initial_count:
            # Removed manual "WARNING - " from message
            logger.warning(f"{self.entity_name} with ID '{entity_id}' not found for deletion in {self.file_path}.")
            raise ValueError(f"{self.entity_name} with ID '{entity_id}' not found for deletion.")
            
        self._write_all(entities_after_deletion)
        # Removed manual "INFO - " from message
        logger.info(f"Successfully deleted {self.entity_name} with ID '{entity_id}' from {self.file_path}.")

