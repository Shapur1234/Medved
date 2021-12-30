import pygame

import globals
import gameobject

def main():
    pygame.init()
    pygame.display.set_caption("🐻 🐻 🐻 Los Medvědos vrací úderos 🐻 🐻 🐻")
    pygame.time.set_timer(pygame.USEREVENT + 1, globals.MovementTick)
    pygame.time.set_timer(pygame.USEREVENT + 2, globals.PhysicsTick)

    screen = pygame.display.set_mode((globals.ScreenWidth, globals.ScreenHeight))

    Play(screen)

def Play(surface) -> None:
    player = gameobject.Player()
    gui = gameobject.GUI()
    world = gameobject.LevelLayout()
    
    running = True
    while running:
        gameUpdated = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT + 1:
                inputMovement = PosChangeFromInput()
                if inputMovement.X != 0 or inputMovement.Y != 0:
                    player.Move(inputMovement, world)
                    inputMovement = gameobject.Vector2D(0, 0)
                    
                    gameUpdated = True
            if event.type == pygame.USEREVENT + 2:
                world.RemoveExpiredSpawns()
                gameUpdated = True
                

        if gameUpdated:
            currentLevel = world.GetLevel(player.WorldPos)
            
            currentLevel.Draw(surface)
            currentLevel.Spawns.Draw(surface)
            player.Draw(surface)

            # surface.blit(someFont.render(f"WorldPos:  {player.WorldPos}", True, (255, 0 ,0)), (16, 16))
            gui.DrawHealthBar(surface, player.Health, player.MaxHealth)

            pygame.display.flip()
            
            # Check for player colliding with spawns
            for count, value in enumerate(currentLevel.Spawns.List):
                if count in currentLevel.Spawns.GetCollidedSpawnIndexes(player.GetRect()):
                    if value.Type == "Salam":
                        player.ModHealth(10)
                        
                        currentLevel.Spawns.List.pop(count)
                    elif value.Type == "Mine":
                        player.ModHealth(-10)
                        currentLevel.Spawns.List += [gameobject.Spawn("Explosion", value.Pos)]
                        
                        currentLevel.Spawns.List.pop(count)
                        
def PosChangeFromInput() -> gameobject.Vector2D:
    pressedKeys = pygame.key.get_pressed()
    return gameobject.Vector2D(0 if pressedKeys[pygame.K_RIGHT] and pressedKeys[pygame.K_LEFT] else 1 if pressedKeys[pygame.K_RIGHT] else -1 if pressedKeys[pygame.K_LEFT] else 0,
                               0 if pressedKeys[pygame.K_DOWN] and pressedKeys[pygame.K_UP] else 1 if pressedKeys[pygame.K_DOWN] else -1 if pressedKeys[pygame.K_UP] else 0)

main()