from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

class App:
    def __init__(self, players, constraint):
        self.players = players
        self.constraint = constraint
        self.player_dict = {}

    def read_player_data(self):
        df = pd.read_csv(self.players)
        df.columns = ["Last Name", "First Name", "Gender", "Birthday", "Skill Level", "Preferred Practice Location", "School", "Parent HC", "Parent AC"]
        df['Birthday'] = pd.to_datetime(df['Birthday'], format='%Y-%m-%d') 
        df.sort_values(by=['Birthday', 'Skill Level'], inplace=True)
        return df

    def get_age_groups(self):
        constraints_df = pd.read_csv(self.constraint)
        age_groups = constraints_df['Age Group'].to_list()
        for index, row in constraints_df.iterrows():
            self.player_dict[f"{row['Age Group']}"] = []
        return age_groups

    def determine_age_group(self, df, age_groups):
        cutoffs = {f"{group}": datetime(datetime.today().year - int(group[2:]), 9, 1) for group in age_groups}
        for index, row in df.iterrows():
            player_birthday = row['Birthday']
            for group, cutoff in cutoffs.items():
                if player_birthday >= cutoff:
                    self.player_dict[group].append(index)
                    break

    def split_into_teams(self, df):
        constraints_df = pd.read_csv(self.constraint)
        max_players_per_team = constraints_df.set_index('Age Group')['Max Players'].to_dict()
        
        teams_dict = {age_group: [] for age_group in max_players_per_team.keys()}
        
        for age_group, players in self.player_dict.items():
            players_data = df.loc[players]
            
            # Separate the data for male and female players for u-8 and above
            if age_group in ['u-8', 'u-10', 'u-12', 'u-14', 'u-16', 'u-18']:
                male_players = players_data[players_data['Gender'] == 'M']
                female_players = players_data[players_data['Gender'] == 'F']
                
                # Sort and split male and female players into separate teams
                sorted_male_players = self.sort_priority_general(male_players)
                sorted_female_players = self.sort_priority_general(female_players)
                
                teams_dict[age_group] = self.assign_teams(sorted_male_players, max_players_per_team[age_group]) + \
                                        self.assign_teams(sorted_female_players, max_players_per_team[age_group])
            else:
                # Handle coed teams for u-5 and u-6
                if age_group == 'u-5':
                    sorted_players = self.sort_priority_u5(players_data)
                elif age_group == 'u-6':
                    sorted_players = self.sort_priority_u6(players_data)
                
                teams_dict[age_group] = self.assign_teams(sorted_players, max_players_per_team[age_group])

        return teams_dict

    # Sort players for u-5 teams
    def sort_priority_u5(self, players_data):
        """
        u-5 priority sorting: Gender (coed) → Practice Location → Skill Level → School → Head Coach → Assistant Coach
        """
        sorted_players = players_data.sort_values(
            by=['Gender', 'Preferred Practice Location', 'Skill Level', 'School', 'Parent HC', 'Parent AC'],
            ascending=[True, True, False, True, False, False]  # Females first, prioritize practice location, then skill
        )
        return sorted_players

    # Sort players for u-6 teams
    def sort_priority_u6(self, players_data):
        """
        u-6 priority sorting: Gender (coed) → School → Skill Level → Practice Location → Head Coach → Assistant Coach
        """
        sorted_players = players_data.sort_values(
            by=['Gender', 'School', 'Skill Level', 'Preferred Practice Location', 'Parent HC', 'Parent AC'],
            ascending=[True, True, False, True, False, False]  # Females first, prioritize school, then skill level
        )
        return sorted_players

    # Sort players for general teams (u-8 and above)
    def sort_priority_general(self, players_data):
        """
        General priority sorting for u-8 and above: School → Skill Level → Practice Location → Head Coach → Assistant Coach
        Gender is not a factor for these teams.
        """
        # Sort using only relevant factors, excluding Gender for non-coed teams
        sorted_players = players_data.sort_values(
            by=['School', 'Skill Level', 'Preferred Practice Location', 'Parent HC', 'Parent AC'],
            ascending=[True, False, True, False, False]  # Prioritize school, skill level, practice location, and coach availability
        )
        return sorted_players

    # Check for gender balance in u-5 and u-6
    def ensure_gender_balance(self, teams_dict, min_girls=2, max_girls=3):
        """
        Ensure that u-5 and u-6 teams have the correct number of girls (between min_girls and max_girls).
        This function will only apply to u-5 and u-6 age groups.
        """
        for age_group, teams in teams_dict.items():
            # Apply gender balance only to u-5 and u-6 teams
            if age_group in ['u-5', 'u-6']:
                for team in teams:
                    girls_in_team = [player for player in team if player['Gender'] == 'F']
                    
                    # Ensure minimum number of girls in the team
                    while len(girls_in_team) < min_girls:
                        # Add a girl to the team if possible
                        pass  # Implement logic to add more girls to the team from other teams
                    
                    # Ensure maximum number of girls in the team
                    while len(girls_in_team) > max_girls:
                        # Move a girl to another team if there are too many
                        pass  # Implement logic to move girls to other teams

    # Ensure coach availability on each team
    def ensure_coach_on_team(self, teams):
        """
        Ensure every team has at  least one head coach or assistant coach.
        """
        for team in teams:
            has_hc = any(player['Parent HC'] == 'Y' for player in team)
            has_ac = any(player['Parent AC'] == 'Y' for player in team)
            
            if not has_hc and not has_ac:
                # Find a coach (head or assistant) to add to the team
                pass  # Implement the logic to add a coach to the team

    def assign_teams(self, sorted_players, max_players):
        """
        Distribute sorted players into teams while respecting the max players per team limit.
        """
        num_teams = len(sorted_players) // max_players + (len(sorted_players) % max_players > 0)
        teams = [[] for _ in range(num_teams)]
        
        team_index = 0
        for _, player in sorted_players.iterrows():
            teams[team_index].append(player.name)
            team_index = (team_index + 1) % num_teams  # Round-robin distribution
        
        return teams
    
    def create_output_csv(self, df, teams_dict, output_file='downloads/output_teams.csv'):
        output_data = []
        for age_group, teams in teams_dict.items():
            for team_index, team in enumerate(teams):
                for player_index in team:
                    player_info = df.loc[player_index].to_dict()
                    player_info['Age Group'] = age_group
                    player_info['Team'] = team_index + 1
                    output_data.append(player_info)

        output_df = pd.DataFrame(output_data)
        output_df.to_csv(output_file, index=False)

    

@app.route('/upload', methods=['POST'])
def upload_files():
    players_file = request.files['players']
    constraints_file = request.files['constraints']
    players_path = os.path.join("uploads", players_file.filename)
    constraints_path = os.path.join("uploads", constraints_file.filename)
    players_file.save(players_path)
    constraints_file.save(constraints_path)

    app_instance = App(players_path, constraints_path)
    df = app_instance.read_player_data()
    age_groups = app_instance.get_age_groups()
    app_instance.determine_age_group(df, age_groups)
    teams_dict = app_instance.split_into_teams(df)
    app_instance.create_output_csv(df, teams_dict)

    return jsonify({"message": "Files processed successfully", "output_file": "output_teams.csv"})

@app.route('/download/output_teams.csv', methods=['GET'])
def download_file(filename="output_teams.csv"):
    return send_from_directory(directory='downloads', path=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)