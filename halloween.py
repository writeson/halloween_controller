# 
# The Fabulous Halloween Controller!
#
import signal 
import asyncio
import random
from gpiozero import LED, MotionSensor


class Scene:
    """This collects all the animations and controls them to
    create a 'scene'
    """
    def __init__(self, queue):
        self.queue = queue
        self.loop = asyncio.get_event_loop()
        self.projector = LED(2, active_high=False) # nightmare before christmas projector
        self.scarecrow = LED(3, active_high=False)
        self.black_ghoul = LED(4, active_high=False)
        self.white_ghoul = LED(27, active_high=False)
        self.jack_o_lanterns = LED(21, active_high=False)
        self.mirror = LED(13, active_high=False)
        self.anim_7 = LED(26, active_high=False)
        self.anim_8 = LED(23, active_high=False)
        self.pir1 = MotionSensor(22)
        self.pir2 = MotionSensor(12)
        self.pir1.when_motion = self.motion_detected
        self.pir2.when_motion = self.motion_detected

        self.animations = [
            self.scarecrow,
            self.black_ghoul,
            self.white_ghoul,
            self.jack_o_lanterns,
            self.mirror,
        ]

    def motion_detected(self):
        """Add a "start animation" flag to the queue from
        the gpiozero when_motion thread
        """
        asyncio.run_coroutine_threadsafe(self.queue.put(True), self.loop)

    async def run_animation(self, animation: LED, duration: float, delay: float=0.0):
        """Run an animation for some time after a delay

        Args:
            animation (LED): The LED (relay) to turn on
            duration (float): How long to keep the relay on
            delay (float, optional): The delay to wait before turning on. Defaults to 0.0.
        """
        await asyncio.sleep(delay)
        animation.on()
        await asyncio.sleep(duration)
        animation.off()

    async def run(self):
        """Run the "scene" This waits for a start True in the queue
        and then builds a list of task animations to run. The projector
        always runs for 2 minutes, the other are short because they
        are momentary buttons that are activated after a delay.
        """
        while True:
            start = await self.queue.get()
            tasks = [self.run_animation(self.projector, 120.0)]
            count = random.randint(3,5)
            tasks.extend([
                self.run_animation(
                    animation, 
                    duration=0.5, 
                    delay=round(random.uniform(1.0, 20.0), 1)
                )
                for animation in random.sample(self.animations, count)
            ])
            await asyncio.gather(*tasks)
            # empty the queue so we don't have to many motion activated 
            # scenes running one after another
            while not self.queue.empty():
                self.queue.get_nowait()


async def main():
    """Create the asyncio queue, passing it to the scene
    constructor and then run the scene asynchronously
    """
    scene = Scene(asyncio.Queue())
    await asyncio.create_task(scene.run())


if __name__ == "__main__":
    asyncio.run(main())
