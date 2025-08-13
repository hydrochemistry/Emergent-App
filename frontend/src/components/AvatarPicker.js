import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const EMOJI_OPTIONS = [
  '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
  '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙',
  '😋', '😛', '😜', '🤪', '😝', '🤗', '🤭', '🤫', '🤔', '🤐',
  '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😌',
  '👨‍💻', '👩‍💻', '🧑‍🎓', '👨‍🎓', '👩‍🎓', '🧑‍🔬', '👨‍🔬', '👩‍🔬',
  '🧑‍💼', '👨‍💼', '👩‍💼', '🧑‍🏫', '👨‍🏫', '👩‍🏫', '🧑‍⚕️', '👨‍⚕️',
  '👩‍⚕️', '🧑‍🎨', '👨‍🎨', '👩‍🎨', '🧠', '🎓', '📚', '📖', '🔬', '⚗️',
  '🧪', '💻', '⌨️', '🖥️', '📊', '📈', '📉', '💡', '🔍', '🔎'
];

const AvatarPicker = ({ currentAvatar, onAvatarChange, onCancel }) => {
  const [selectedAvatar, setSelectedAvatar] = useState(currentAvatar || '');

  const handleSave = () => {
    onAvatarChange(selectedAvatar);
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Choose Your Avatar</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Current Avatar:</p>
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center text-2xl">
            {selectedAvatar || '😀'}
          </div>
        </div>
        
        <div className="grid grid-cols-8 gap-2 mb-4 max-h-64 overflow-y-auto">
          {EMOJI_OPTIONS.map((emoji, index) => (
            <button
              key={index}
              onClick={() => setSelectedAvatar(emoji)}
              className={`w-10 h-10 text-xl hover:bg-blue-100 rounded-lg transition-colors ${
                selectedAvatar === emoji ? 'bg-blue-200 ring-2 ring-blue-500' : 'hover:bg-gray-100'
              }`}
            >
              {emoji}
            </button>
          ))}
        </div>
        
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            Save Avatar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default AvatarPicker;