#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# HorseGame
# Copyright (C) 2008, ghopper
# Copyright (C) 2012 Alan Aguiar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Alan Aguiar <alanjas@gmail.com>

import gtk
import pygame
import logging
import math
import random


class Game():

    def __init__(self):
        self.game_running = True
        # tuple for horse location
        self.horse_loc = (100,100)
        # array of (image,location) for apple/carrot/etc locations
        self.objects = []
        # keep track of the mouse pointer
        self.mouse_pos = (300,300)
        # tuple size
        self.screen_size = (1200,900)
        self.grass_size = (0,0)
        self.horse_size = (0,0)
        self.apple_size = (0,0)
        # images / (type pygame Surface)
        self.background = None
        self.grass_image = None
        self.horse_image = None
        self.horse_image_l = None
        self.moving_left = False
        self.apple_image = None
        self.carrot_image = None
        self.hay_image = None
        # other parameters
        self.horse_speed = 8 # pixels per tick; at 25 ticks/second, this is approx 200 pixels per second
        self.horse_reach = 20 # pixels from cener of horse where he can reach
        self.target_loc = None
    
    def setup(self):
        self.screen_size = self.screen.get_size() # tuple
        # load the images and convert to screen format
        self.grass_image = pygame.image.load('images/grass.png','grass')
        self.grass_image.convert(self.screen)
        self.grass_size = self.grass_image.get_size()
        self.horse_image = pygame.image.load('images/horse.png','horse')
        self.horse_image.convert(self.screen)
        self.horse_size = self.horse_image.get_size()
        # Make a copy for the left-facing image
        self.horse_image_l=pygame.transform.flip(self.horse_image,True,False)
        # Make the edibles
        self.apple_size = (10,10)
        self.apple_image = pygame.Surface(self.apple_size, 0, self.screen)
        self.apple_image.fill((0xff,0,0))
        self.carrot_size = (7,20)
        self.carrot_image = pygame.Surface(self.carrot_size, 0, self.screen)
        self.carrot_image.fill((0xff,0x99,0))
        self.hay_size = (20,20)
        self.hay_image = pygame.Surface(self.hay_size, 0, self.screen)
        self.hay_image.fill((0x99,0x66,0x33))

        self.background = pygame.Surface((self.screen_size[0], self.screen_size[1]), 0, self.screen)

        tilex=int(math.ceil(self.screen_size[0]/float(self.grass_size[0])))
        tiley=int(math.ceil(self.screen_size[1]/float(self.grass_size[1])))
        for x in range(0,tilex):
            for y in range(0,tiley):
                self.background.blit(self.grass_image,(x*self.grass_size[0],y*self.grass_size[1]))

        self.update()

    def update(self):
        """updates the screen image"""
        self.screen.blit(self.background, (0,0))

        # draw apples and other objects
        for o in self.objects:
            self.drawObject(o)

        if self.moving_left:
            self.drawObject((self.horse_image_l, self.horse_loc))
        else:
            self.drawObject((self.horse_image, self.horse_loc))

        # flip display buffer
        pygame.display.flip()
        
    def drawObject(self, o):
        # unpack the object
        (image, loc) = o
        object_size = image.get_size()
        # adjust the upper left corner so that the center of object is at the recorded location
        adj_loc = (loc[0]-object_size[0]/2,loc[1]-object_size[1]/2)
        self.screen.blit(image, adj_loc)
        
    def placeObject(self, image, location):
        #adj_loc = self.adjust_loc(location, image.get_size())
        #adj_loc = location
        self.objects.append((image, location))

    def adjust_loc(self,loc,object_size):
        """adjust the given location by half the object size.  Thus the center of the object will be at loc"""
        adj_loc = (loc[0]-object_size[0]/2,loc[1]-object_size[1]/2)
        return adj_loc
        
    def handleEvent(self,event):
        if event.type == pygame.QUIT:
            self.game_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (27,113): # esc or q=quit
                self.game_running = False
            elif event.key == 97: # a=apple
                self.placeObject(self.apple_image,  self.mouse_pos)
            elif event.key == 99: # c=carrot
                self.placeObject(self.carrot_image,  self.mouse_pos)
            elif event.key == 104: # h=hay
                self.placeObject(self.hay_image,  self.mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # place apples
            self.placeObject(self.apple_image,  self.mouse_pos)
        elif event.type == pygame.MOUSEMOTION:
            # Remember mouse location, because we need it in KEYDOWN events
            self.mouse_pos = event.pos
    
    def tick(self,millis):
        """updates the game state for a tick"""
        # millis is ignored
        if len(self.objects)>0:
            # move the horse toward the first object in the queue, at full speed
            (target_image,target_loc) = self.objects[0]
            horse_speed = self.horse_speed
        else:
            # the horse might feel inclined to wander slowly toward a random target
            #if self.target_loc is None:
            #    self.target_loc = (self.screen_size[0]*random.random(), self.screen_size[1]*random.random())
            #target_loc = self.target_loc
            
            # wander toward mouse
            target_loc = self.mouse_pos
            horse_speed = 2
            
        (distx, disty) = (target_loc[0] - self.horse_loc[0], target_loc[1] - self.horse_loc[1])
        # TODO: there is probably a library function to scale this for me
        # move the horse approx horse_speed pixels in the indicated direction
        dist = math.sqrt(distx*distx+disty*disty)
        (movex, movey) = (horse_speed*distx/dist, horse_speed*disty/dist)

        # "eat" the object if we are close enough
        # (so that we will get a new target next tick)
        # TODO: perhaps colision detection would be better here
        if dist < self.horse_speed*2:
            if len(self.objects)>0:
                self.objects.pop(0)
            else:
                self.target_loc = None
                # dont move the horse (causes bounce)
                return

        # move the horse, but check that the horse has not wandered off the screen
        (horsex, horsey) = (self.horse_loc[0] + movex, self.horse_loc[1] + movey)
        # TODO: check for a library function to determine out of bounds
        if (horsex < 0):
            horsex = 0
        if (horsey < 0):
            horsey = 0
        if (horsex > self.screen_size[0]):
            horsex = self.screen_size[0]
        if (horsey > self.screen_size[1]):
            horsey = self.screen_size[1]
        self.horse_loc = (horsex,horsey)
        
        if movex<0 and abs(distx)>horse_speed:
            self.moving_left = True
        else:
            self.moving_left = False

    def run(self):
        self.screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        self.setup()

        while self.game_running:
            #GTK events
            while gtk.events_pending():
                gtk.main_iteration()

            # tick with wait 1/25th of a second
            milliseconds = clock.tick(25)
            self.tick(milliseconds)
            self.update()

            events = pygame.event.get()
            for event in events:
                self.handleEvent(event)


