
import cocos
from cocos.scene import Scene
from HUD import HUD
from GameModel import GameModel
from GameController import GameController


__all__ = ['get_newgame']


class GameView(cocos.layer.ColorLayer):
    is_event_handler = True  #: enable director.window events

    def __init__(self, model, hud):
        super(GameView, self).__init__(64, 64, 224, 0)
        model.set_view(self)
        self.hud = hud
        self.model = model
        self.model.push_handlers(self.on_update_objectives)
        self.model.start()
        self.hud.set_objectives(self.model.objectives)
        self.hud.show_message('GET READY')

    def on_update_objectives(self):
        self.hud.set_objectives(self.model.objectives)

def get_newgame():


    scene = Scene()
    model = GameModel()
    controller = GameController(model)
    # view
    hud = HUD()
    view = GameView(model, hud)

    # set controller in model
    model.set_controller(controller)

    # add controller
    scene.add(controller, z=1, name="controller")
    scene.add(hud, z=3, name="hud")
    scene.add(view, z=2, name="view")

    return scene