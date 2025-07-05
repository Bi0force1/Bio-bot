# setup imports
import discord
from discord.ext import commands
import random


reps = [
    ("[Burpees](https://i0.wp.com/joshuaspodek.com/wp-content/uploads/2012/12/burpees1.png?ssl=1)",),
    ("[Crunches - Lay Down](https://cdn.shopify.com/s/files/1/0982/0194/files/5bestworkouttodowithwaisttrainers_3.jpg?v=1642018436)",),
    ("[Crunches - Standing side](https://liftmanual.com/wp-content/uploads/2023/04/standing-side-crunch.jpg)",),
    ("[Crunches - Standing](https://www.spotebi.com/wp-content/uploads/2015/12/standing-criss-cross-crunches-exercise-illustration.jpg)",),
    ("[Crunches - Table](https://www.mindfood.com/wp-content/uploads/2016/10/table-top-knee-crunch_081_83.jpg)",),
    ("[Dumbbell - Bicep Curl](https://fitwill.app/cdn-cgi/image/width=750,quality=75,format=auto/https://fitwill.app/api/image/0285?w=1024&h=576)",),
    ("[Dumbbell - Chest Fly](https://bod-blog-assets.prod.cd.beachbodyondemand.com/bod-blog/wp-content/uploads/2022/07/12111451/dumbbell-chest-fly-600-demo.jpg)",),
    ("[dumbbell - Chest Press](https://hips.hearstapps.com/hmg-prod/images/floor-press-1586948016.jpg?resize=980:*)",),
    ("[Dumbbell - Cross Body Curl](https://fitwill.app/cdn-cgi/image/width=750,quality=75,format=auto/https://fitwill.app/api/image/1657?w=1024&h=576)",),
    ("[Dumbbell - Front Raise](https://liftmanual.com/wp-content/uploads/2023/04/dumbbell-front-raise.jpg)",),
    ("[Dumbbell - Overhead Press](https://fitwill.app/cdn-cgi/image/width=750,quality=75,format=auto/https://fitwill.app/api/image/0426?w=1024&h=576)",),
    ("[Dumbbell - Side Raise](https://gymgeek.com/wp-content/uploads/2024/02/dumbbell-lateral-raises-square.png)",),
    ("[Dumbbell - Tricep Press](https://training.fit/wp-content/uploads/2020/03/trizepsdruecken-einarmig-kurzhantel.png)",),
    ("[Elastic bands - Curls](https://s3assets.skimble.com/assets/2332037/image_iphone.jpg)",),
    ("[Elastic Bands - Forward Chest Press](https://bodylastics.com/wp-content/uploads/2022/07/pf-8ec9e0d9-OneArmChestPressWithTubeBands-1-768x768.webp)",),
    ("[Elastic bands - Forward Pull Downs](https://pump-app.s3.eu-west-2.amazonaws.com/exercise-assets/09741101-Band-close-grip-pulldown_Back_small.jpg)",),
    ("[Elastic bands - Overhead Press](https://cdn.vectorstock.com/i/2000v/05/99/man-doing-resistance-band-standing-shoulder-press-vector-49590599.avif)",),
    ("[Elastic bands - Side Pull Downs](https://liftmanual.com/wp-content/uploads/2023/04/band-straight-arm-pulldown.jpg)",),
    ("[Jump Rope](https://www.realsimple.com/thmb/vkvtaAlP95xvlNBjdrSEwUzlKGA=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/JumpRope_1-0667b2baaa214633af1b1c88c69e579a.png)",),
    ("[Lunges - Forward](https://www.spotebi.com/wp-content/uploads/2016/09/front-and-back-lunges-exercise-illustration-spotebi.jpg)",),
    ("[Lunges - Side](https://blog.fizzup.com/wp-content/uploads/2017/08/SideLunges-1.png)",),
    ("[Push ups](https://content.artofmanliness.com/uploads/2020/11/Pushup-Re-do-1-768x512.jpg)",),
    ("[Sit Ups](https://d3srkhfokg8sj0.cloudfront.net/wp-content/uploads/1120_STD_AskTrainer_IMG1.jpg)",),
    ("[Sit Ups - Twist](https://wwws.fitnessrepublic.com/wp-content/uploads/2015/06/russian-twist-move.jpg)",),
    ("[Squats](https://www.besthealthmag.ca/wp-content/uploads/2008/10/how-to-do-squats-properly-.jpg?resize=768%2C512)",)
]


holds = [
    ("[Down Dog](https://www.ekhartyoga.com/media/images/articles/content/Downward-Facing-Dog-Pose-Adho-Mukha-Svanasana.jpg)",),
    ("[Down Dog to Plank](https://images.ctfassets.net/p0sybd6jir6r/5sD6NBz2zoPfYAEDblMu5C/57dd98575fd9937e6bc7ebf9a0aeac29/dolphin-flow.png)",),
    ("[Pigeon Pose](https://lh4.googleusercontent.com/CqH7eprlquNVUpNyxFMTl6SoFhuCY8rthT82PwhXQEU_K2waIzCPBfoTt0lMND8p-wqs2eNCR489uq1J5Yu0rwQaGc4-nQyLtto6Me2QUZP0P_okd6z0BySgUKZ1jphLvCeEymDw)",),
    ("[Plank - Forward](https://www.wikihow.com/images/thumb/c/cb/How-Long-to-Hold-a-Plank-As-a-Beginner-Step-8.jpg/v4-728px-How-Long-to-Hold-a-Plank-As-a-Beginner-Step-8.jpg)",),
    ("[Plank - Raise arm](https://images.squarespace-cdn.com/content/v1/5750d5129f72662d66448028/1513303476833-0JZ803QA3Z7DNJ4IHZLP/Single+Arm+Plank+2.jpg?format=1500w)",),
    ("[Plank - Side](https://images.squarespace-cdn.com/content/v1/5d31ed671abe780001b2964d/1604695972703-K37B5ZAVVV6FU6L62I7U/Jacy+Cunningham+doing+Forearm+Side+Plank?format=1000w)",),
]


weight = [
    "5",
    "8",
    "10",
    "12",
    "15",
    "20"
]


time = [
    ":15",
    ":20",
    ":30",
    ":45",
    ":60",
    "1:15",
    "1:30",
    "1:45",
    "2:00"
]


class Workout(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def workout(self, ctx):

        response = ""

        for i in range(3):
            selection = random.choice(["reps", "holds"])

            if selection == "reps":
                exercise = random.choice(reps)
                weight_value = random.choice(weight)
                response += f"\nExercise {i + 1}: {exercise[0]}\nReps: {weight_value}\n"
            else:
                exercise = random.choice(holds)
                time_value = random.choice(time)
                response += f"\nExercise {i + 1}: {exercise[0]}\nTime: {time_value}\n"

        await ctx.author.send(response)


async def setup(client):
    await client.add_cog(Workout(client))

