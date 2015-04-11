import entities
import pygame
import ordered_list
from actions import *
import random
import occ_grid
import point
import image_store

class WorldModel:
   def __init__(self, num_rows, num_cols, background):
      self.background = occ_grid.Grid(num_cols, num_rows, background)
      self.num_rows = num_rows
      self.num_cols = num_cols
      self.occupancy = occ_grid.Grid(num_cols, num_rows, None)
      self.entities = []
      self.action_queue = ordered_list.OrderedList()


   def within_bounds(self, pt):
      return (pt.x >= 0 and pt.x < self.num_cols and
         pt.y >= 0 and pt.y < self.num_rows)


   def is_occupied(self, pt):
      return (self.within_bounds(pt) and
         occ_grid.Grid.get_cell(self.occupancy, pt) != None)

   def find_nearest(self, pt, type):
      oftype = [(e, distance_sq(pt, e.get_position()))
         for e in self.entities if isinstance(e, type)]

      return nearest_entity(oftype)


   def add_entity(self, entity):
      pt = entity.get_position()
      if self.within_bounds(pt):
         old_entity = occ_grid.Grid.get_cell(self.occupancy, pt)
         if old_entity != None:
            entities.clear_pending_actions(old_entity)
         occ_grid.Grid.set_cell(self.occupancy, pt, entity)
         self.entities.append(entity)


   def move_entity(self, entity, pt):
      tiles = []
      if self.within_bounds(pt):
         old_pt = entity.get_position()
         occ_grid.Grid.set_cell(self.occupancy, old_pt, None)
         tiles.append(old_pt)
         occ_grid.Grid.set_cell(self.occupancy, pt, entity)
         tiles.append(pt)
         entity.set_position(pt)

      return tiles


   def remove_entity(self, entity):
      self.remove_entity_at(entity.get_position())


   def remove_entity_at(self, pt):
      if (self.within_bounds(pt) and
         occ_grid.Grid.get_cell(self.occupancy, pt) != None):
         entity = occ_grid.Grid.get_cell(self.occupancy, pt)
         entity.set_position(point.Point(-1, -1))
         self.entities.remove(entity)
         occ_grid.Grid.set_cell(self.occupancy, pt, None)


   def schedule_action(self, action, time):
      self.action_queue.insert(action, time)


   def unschedule_action(self, action):
      self.action_queue.remove(action)

   def get_background_image(self, pt):
      if self.within_bounds(pt):
         e = occ_grid.Grid.get_cell(self.background, pt)
         return e.get_image()


   def get_background(self, pt):
      if self.within_bounds(pt):
         return occ_grid.Grid.get_cell(world.background, pt)


   def set_background(self, pt, bgnd):
      if self.within_bounds(pt):
         occ_grid.Grid.set_cell(self.background, pt, bgnd)


   def get_tile_occupant(self, pt):
      if self.within_bounds(pt):
         return occ_grid.Grid.get_cell(self.occupancy, pt)


   def get_entities(self):
      return self.entities

   def update_on_time(self, ticks):
      tiles = []

      next = self.action_queue.head()
      while next and next.ord < ticks:
         self.action_queue.pop()
         tiles.extend(next.item(ticks))  # invoke action function
         next = self.action_queue.head()

      return tiles

   def create_blob(self, name, pt, rate, ticks, i_store):
      blob = entities.OreBlob(name, pt, rate,
         image_store.get_images(i_store, 'blob'),
         random.randint(BLOB_ANIMATION_MIN, BLOB_ANIMATION_MAX)
         * BLOB_ANIMATION_RATE_SCALE)
      blob.schedule_blob(self, ticks, i_store)
      return blob


   def create_vein(self, name, pt, ticks, i_store):
      vein = entities.Vein("vein" + name,
         random.randint(VEIN_RATE_MIN, VEIN_RATE_MAX),
         pt, image_store.get_images(i_store, 'vein'))
      return vein

   def create_ore(self, name, pt, ticks, i_store):
      ore = entities.Ore(name, pt, image_store.get_images(i_store, 'ore'),
         random.randint(ORE_CORRUPT_MIN, ORE_CORRUPT_MAX))
      ore.schedule_ore(self, ticks, i_store)

      return ore

   def create_quake(self, pt, ticks, i_store):
      quake = entities.Quake("quake", pt,
         image_store.get_images(i_store, 'quake'), QUAKE_ANIMATION_RATE)
      quake.schedule_quake(self, ticks)
      return quake

def nearest_entity(entity_dists):
   if len(entity_dists) > 0:
      pair = entity_dists[0]
      for other in entity_dists:
         if other[1] < pair[1]:
            pair = other
      nearest = pair[0]
   else:
      nearest = None

   return nearest


def distance_sq(p1, p2):
   return (p1.x - p2.x)**2 + (p1.y - p2.y)**2

